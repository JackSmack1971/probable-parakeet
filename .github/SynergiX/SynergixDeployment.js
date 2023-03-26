const SynergiXStaking = await ethers.getContractFactory("SynergiXStaking");
const staking = await SynergiXStaking.deploy(token.address);
await staking.deployed(); 

const SynergiXToken = await ethers.getContractFactory("SynergiXToken");
const token = await SynergiXToken.deploy(staking.address);
await token.deployed();
