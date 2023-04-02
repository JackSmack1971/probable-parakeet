pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract SimpleNFT is ERC721, Ownable {
    using Counters for Counters.Counter;

    Counters.Counter private _tokenIdCounter;

    string public baseURI;
    string public hiddenMetadataURI;

    uint256 public constant MAX_SUPPLY = 10000;
    uint256 public constant MAX_MINT_AMOUNT = 5;
    uint256 public cost = 0.01 ether;

    bool public mintPaused;
    bool public revealed;

    constructor(string memory name_, string memory symbol_)
        ERC721(name_, symbol_)
    {}

    function mint(uint256 amount) public payable {
        require(!mintPaused, "Minting is paused");
        require(
            amount > 0 && amount <= MAX_MINT_AMOUNT,
            "Invalid mint amount"
        );
        require(
            totalSupply() + amount <= MAX_SUPPLY,
            "Max supply exceeded"
        );
        require(
            msg.value >= cost * amount,
            "Insufficient payment"
        );

        for (uint256 i = 0; i < amount; i++) {
            _safeMint(msg.sender, _tokenIdCounter.current());
            _tokenIdCounter.increment();
        }
    }

    function mintForAddress(uint256 amount, address recipient)
        public
        onlyOwner
    {
        require(
            amount > 0 && amount <= MAX_MINT_AMOUNT,
            "Invalid mint amount"
        );
        require(
            totalSupply() + amount <= MAX_SUPPLY,
            "Max supply exceeded"
        );

        for (uint256 i = 0; i < amount; i++) {
            _safeMint(recipient, _tokenIdCounter.current());
            _tokenIdCounter.increment();
        }
    }

    function setMintPaused(bool paused) public onlyOwner {
        mintPaused = paused;
    }

    function setRevealed(bool _state) public onlyOwner {
        revealed = _state;
    }

    function setCost(uint256 _cost) public onlyOwner {
        cost = _cost;
    }

    function setBaseURI(string memory uri) public onlyOwner {
        baseURI = uri;
    }

    function setHiddenMetadataURI(string memory uri) public onlyOwner {
        hiddenMetadataURI = uri;
    }

    function withdraw() public onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "Insufficient balance");

        uint256 hashLipsFee = (balance * 5) / 100;
        (bool success, ) = payable(0x943590A42C27D08e3744202c4Ae5eD55c2dE240D).call{value: hashLipsFee}("");
        require(success, "Failed to transfer HashLips fee");

        (success, ) = payable(owner()).call{value: balance - hashLipsFee}("");
        require(success, "Failed to transfer remaining balance");
    }

    function totalSupply() public view returns (uint256) {
        return _tokenIdCounter.current();
    }

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_exists(tokenId), "Token does not exist");

        if (!revealed) {
            return hiddenMetadataURI;
        }

        string memory uri = baseURI;
        if (bytes(uri).length == 0) {
            return "";
        }

        return string(abi.encodePacked(uri, tokenId.toString(), ".json"));
}
}
