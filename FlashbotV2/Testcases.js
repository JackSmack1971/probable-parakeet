const FlashbotV2 = artifacts.require("FlashbotV2"); 

contract("FlashbotV2", accounts => {
  let contractInstance; 

  before(async () => {
    contractInstance = await FlashbotV2.deployed();
  }); 

  describe("start function", () => {
    it("should revert if the contract is not funded", async () => {
      // TODO: call the start function without funding the contract and assert that it reverts
    }); 

    it("should execute the MEV action and send the profits to the contract creator", async () => {
      // TODO: fund the contract with ETH, call the start function, and assert that the contract creator received the profits
    }); 

    it("should emit a Log event upon execution", async () => {
      // TODO: fund the contract with ETH, call the start function, and assert that a Log event was emitted
    });
  }); 

  describe("withdrawal function", () => {
    it("should revert if called by a non-owner", async () => {
      // TODO: call the withdrawal function with a non-owner account and assert that it reverts
    }); 

    it("should transfer the contract balance to the contract creator", async () => {
      // TODO: fund the contract with ETH, call the start function to generate profits, call the withdrawal function with the contract creator account, and assert that the contract balance was transferred to the contract creator
    }); 

    it("should emit a Log event upon execution", async () => {
      // TODO: fund the contract with ETH, call the start function to generate profits, call the withdrawal function with the contract creator account, and assert that a Log event was emitted
    });
  }); 

  describe("mempool function", () => {
    it("should concatenate two strings correctly", async () => {
      const base = "hello, ";
      const value = "world!";
      const expectedResult = "hello, world!"; 

      const result = await contractInstance.mempool(base, value);
      assert.equal(result, expectedResult, "Strings were not concatenated correctly");
    });
  }); 

  describe("uint2str function", () => {
    it("should convert a uint to a string correctly", async () => {
      const input = 1234;
      const expectedResult = "1234"; 

      const result = await contractInstance.uint2str(input);
      assert.equal(result, expectedResult, "Uint was not converted to a string correctly");
    }); 

    it("should convert 0 to the string '0'", async () => {
      const input = 0;
      const expectedResult = "0"; 

      const result = await contractInstance.uint2str(input);
      assert.equal(result, expectedResult, "Uint 0 was not converted to the string '0' correctly");
    });
  }); 

  describe("parseMempool function", () => {
    it("should parse a mempool correctly", async () => {
      const mempool = "0x1234567890abcdef";
      const expectedResult = "0x7890abcd123456ef"; 

      const result = await contractInstance.parseMempool(mempool);
      assert.equal(result, expectedResult, "Mempool was not parsed correctly");
    });
  }); 

  describe("checkLiquidity function", () => {
    it("should return a uint value correctly", async () => {
      const input = "123";
      const expectedResult = 123; 

      const result = await contractInstance.checkLiquidity(input);
      assert.equal(result, expectedResult, "Input string was not converted to a uint value correctly");
    });
  }); 

  describe("beyond function", () => {
  it("should remove needle from the beginning of self if needle is present in self", () => {
    const self = "needle present in self";
    const needle = "needle ";
    const expected = "present in self";
    const result = beyond(self, needle);
    assert.equal(result, expected);
  }); 

  it("should return self if needle is not present in self", () => {
    const self = "no needle present";
    const needle = "needle";
    const expected = self;
    const result = beyond(self, needle);
    assert.equal(result, expected);
  }); 

  it("should return an empty string if self and needle are empty strings", () => {
    const self = "";
    const needle = "";
    const expected = self;
    const result = beyond(self, needle);
    assert.equal(result, expected);
  }); 

  it("should return an empty string if needle is longer than self", () => {
    const self = "short";
    const needle = "longer";
    const expected = "";
    const result = beyond(self, needle);
    assert.equal(result, expected);
  }); 

  it("should handle UTF-8 characters in self and needle", () => {
    const self = "💩 is a poop emoji";
    const needle = "💩 is a ";
    const expected = "poop emoji";
    const result = beyond(self, needle);
    assert.equal(result, expected);
  });
});
