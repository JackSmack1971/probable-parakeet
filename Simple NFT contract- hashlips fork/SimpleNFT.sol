// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0; 

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721Receiver.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/IERC721Metadata.sol";
import "@openzeppelin/contracts/token/ERC721/utils/ERC721Holder.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
import "@openzeppelin/contracts/utils/introspection/IERC165.sol";
import "@openzeppelin/contracts/utils/introspection/ERC165.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/IERC721Enumerable.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/IERC721Metadata.sol";
import "@openzeppelin/contracts/utils/Address.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/IERC20Metadata.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/IERC20Permit.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Snapshot.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/structs/BitMaps.sol";
import "@openzeppelin/contracts/utils/structs/ReverseEnumerableMap.sol"; 

contract SimpleNFT is IERC721, IERC721Receiver, ERC165, ERC721Holder, IERC721Metadata, Ownable, ReentrancyGuard {
    using SafeMath for uint256;
    using Counters for Counters.Counter;
    using SafeERC20 for IERC20;
    using Address for address;
    using EnumerableSet for EnumerableSet.UintSet;
    using EnumerableMap for EnumerableMap.UintToAddressMap;
    using BitMaps for BitMaps.BitMap;
    using ReverseEnumerableMap for EnumerableMap.UintToAddressMap; 

    // Constants
    uint256 private constant MAX_SUPPLY = 10000;
    uint256 private constant MAX_MINT_AMOUNT = 5;
    uint256 private constant MAX_TOKEN_COST = 1 ether;
    uint256 private constant MAX_MINT_PER_ADDRESS = 50;
    uint256 private constant VESTING_PERIOD = 365 days;
    uint256 private constant VESTING_CLIFF = 90 days; 

    // Variables
    Counters.Counter private _tokenIdCounter;
    uint256 private _cost = 0.01 ether;
    string private _baseURI;
    string private _hiddenMetadataURI;
    bool private _mintPaused;
    bool private _revealed;
    BitMaps.BitMap private _whitelist;
    mapping(uint256 => uint256) private _royalties;
    mapping(address => uint256) private _mintedCount;
mapping(address => uint256) private _vestedBalance;
mapping(address => uint256) private _lastVestingTime; 

// Events
event Minted(address indexed to, uint256 indexed tokenId, uint256 amount);
event CostChanged(uint256 cost);
event BaseURIChanged(string baseURI);
event HiddenMetadataURIChanged(string hiddenMetadataURI);
event MintPaused(bool paused);
event Revealed(bool state);
event WhitelistAdded(address indexed account);
event WhitelistRemoved(address indexed account);
event RoyaltiesSet(uint256 indexed tokenId, uint256 percentage); 

constructor(string memory name_, string memory symbol_)
    ERC721(name_, symbol_)
{} 

function mint(uint256 amount) public payable nonReentrant {
    require(!_mintPaused, "Minting is paused");
    require(_whitelist.get(msg.sender) || amount > 0, "Invalid mint amount");
    require(amount.add(_mintedCount[msg.sender]) <= MAX_MINT_PER_ADDRESS, "Exceeded maximum mint per address");
    require(
        amount <= MAX_MINT_AMOUNT,
        "Exceeded maximum mint amount"
    );
    require(
        totalSupply().add(amount) <= MAX_SUPPLY,
        "Exceeded maximum supply"
    );
    require(
        msg.value >= _cost.mul(amount),
        "Insufficient payment"
    ); 

    for (uint256 i = 0; i < amount; i++) {
        _safeMint(msg.sender, _tokenIdCounter.current());
        _tokenIdCounter.increment();
    } 

    _mintedCount[msg.sender] = _mintedCount[msg.sender].add(amount); 

    emit Minted(msg.sender, _tokenIdCounter.current().sub(1), amount);
} 

function mintForAddress(uint256 amount, address recipient) public onlyOwner {
    require(
        amount > 0 && amount <= MAX_MINT_AMOUNT,
        "Invalid mint amount"
    );
    require(
        totalSupply().add(amount) <= MAX_SUPPLY,
        "Exceeded maximum supply"
    ); 

    for (uint256 i = 0; i < amount; i++) {
        _safeMint(recipient, _tokenIdCounter.current());
        _tokenIdCounter.increment();
        _vestedBalance[recipient] = _vestedBalance[recipient].add(1);
        _lastVestingTime[recipient] = block.timestamp;
    } 

    emit Minted(recipient, _tokenIdCounter.current().sub(amount), amount);
} 

function setCost(uint256 cost) public onlyOwner {
    require(cost <= MAX_TOKEN_COST, "Cost exceeds maximum");
    _cost = cost;
    emit CostChanged(cost);
} 

function setBaseURI(string memory baseURI) public onlyOwner {
    _baseURI = baseURI;
    emit BaseURIChanged(baseURI);
} 

function setHiddenMetadataURI(string memory hiddenMetadataURI)
    public
    onlyOwner
{
    _hiddenMetadataURI = hiddenMetadataURI;
    emit HiddenMetadataURIChanged(hiddenMetadataURI);
} 

function setMintPaused(bool paused) public onlyOwner {
    _mintPaused = paused;
    emit MintPaused(paused);
} 

function setRevealed(bool state) public onlyOwner {
    _revealed = state;
    emit Revealed(state);
} 

function addToWhitelist(address account) public onlyOwner {
    require(account != address(0), "Invalid address");
    require(!_whitelist.get(account), "Account already whitelisted"); 

    _whitelist.set(account, true); 

    emit WhitelistAdded(account);
} 

function removeFromWhitelist(address account) public onlyOwner {
    require(account != address(0), 

    require(_whitelist.get(account), "Account not whitelisted"); 

    _whitelist.set(account, false); 

    emit WhitelistRemoved(account);
} 

function setRoyalties(uint256 tokenId, uint256 percentage) public onlyOwner {
    require(_exists(tokenId), "Token does not exist");
    require(percentage <= 100, "Percentage exceeds maximum"); 

    _royalties[tokenId] = percentage; 

    emit RoyaltiesSet(tokenId, percentage);
} 

function totalSupply() public view override returns (uint256) {
    return _tokenIdCounter.current();
} 

function tokenURI(uint256 tokenId)
    public
    view
    override(ERC721URIStorage, IERC721Metadata)
    returns (string memory)
{
    require(_exists(tokenId), "Token does not exist"); 

    if (!_revealed) {
        return _hiddenMetadataURI;
    } 

    string memory uri = ERC721URIStorage.tokenURI(tokenId);
    if (bytes(_baseURI).length == 0) {
        return uri;
    } else {
        return string(abi.encodePacked(_baseURI, uri));
    }
} 

function royaltyInfo(uint256 tokenId, uint256 value) public view returns (address, uint256) {
    require(_exists(tokenId), "Token does not exist"); 

    uint256 percentage = _royalties[tokenId];
    if (percentage == 0) {
        return (address(0), 0);
    } else {
        uint256 amount = value.mul(percentage).div(100);
        return (ownerOf(tokenId), amount);
    }
} 

function burn(uint256 tokenId) public {
    require(_exists(tokenId), "Token does not exist");
    require(_isApprovedOrOwner(msg.sender, tokenId), "Caller is not owner nor approved"); 

    _burn(tokenId);
} 

function transfer(address to, uint256 tokenId) public virtual override {
    _transfer(msg.sender, to, tokenId);
    _vestedBalance[msg.sender] = _vestedBalance[msg.sender].sub(1);
    _vestedBalance[to] = _vestedBalance[to].add(1);
    _lastVestingTime[to] = block.timestamp;
} 

function _beforeTokenTransfer(
    address from,
    address to,
    uint256 tokenId
) internal virtual override {
    super._beforeTokenTransfer(from, to, tokenId);
    if (from == address(0)) {
        // minting
        return;
    } 

    // Calculate vested balance for sender
    if (_vestedBalance[from] > 0) {
        uint256 vestedAmount = calculateVestedAmount(from);
        if (_vestedBalance[from] <= vestedAmount) {
            _vestedBalance[from] = 0;
        } else {
            _vestedBalance[from] = _vestedBalance[from].sub(vestedAmount);
        }
    } 

    // Calculate vested balance for recipient
    if (_vestedBalance[to] > 0) {
        uint256 vestedAmount = calculateVestedAmount(to);
        _vestedBalance[to] = _vestedBalance[to].add(vestedAmount);
    }
} 

function calculateVestedAmount(address account) private view returns (uint256) { uint256 vestedBalance = _vestedBalance[account]; if (vestedBalance == 0) { return 0; } uint256 vestingStartTime = _lastVestingTime[account]; uint256 elapsedTime = block.timestamp.sub(vestingStartTime); if (elapsedTime >= VESTING_PERIOD) { return vestedBalance; } uint256 vestingDuration = VESTING_PERIOD.sub(VESTING_CLIFF); uint256 vestedPerDay = vestedBalance.div(vestingDuration); return elapsedTime.mul(vestedPerDay); }
}
