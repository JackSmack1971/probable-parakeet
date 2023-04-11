// GameChain Token (GMC) Smart Contract
// ERC20 Token Standard 

pragma solidity ^0.8.0; 

contract GameChainToken {
    // Token Information
    string public constant name = "GameChain";
    string public constant symbol = "GMC";
    uint8 public constant decimals = 18;
    uint256 public totalSupply; 

    // Mappings
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    mapping(address => uint256) public stakedBalance;
    mapping(address => uint256) public lastStakeTimestamp;
    mapping(address => bool) public isGameDeveloper;
    mapping(address => bool) public isBugReporter;
    mapping(address => uint256) public contributionRewards;
    mapping(address => uint256) public liquidityRewards;
    mapping(address => uint256) public lockedStakes; 

    // Events
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event Staked(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event Locked(address indexed user, uint256 amount);
    event Unlocked(address indexed user, uint256 amount);
    event ContributionReward(address indexed user, uint256 amount);
    event LiquidityReward(address indexed user, uint256 amount); 

    // Rewards Parameters
    uint256 public constant REWARD_RATE = 10; // 10% annual rewards
    uint256 public constant REWARD_INTERVAL = 365 days;
    uint256 public constant STAKE_LOCK_PERIOD = 90 days;
    uint256 public constant MIN_STAKE_AMOUNT = 1000 * 10 ** uint256(decimals);
    uint256 public constant LIQUIDITY_REWARD_RATE = 2; // 2% of trade volume 

    // Governance Parameters
    uint256 public constant MIN_PROPOSAL_THRESHOLD = 100000 * 10 ** uint256(decimals); // Minimum tokens required to submit a proposal
    uint256 public constant VOTING_PERIOD = 7 days;
    uint256 public constant VOTING_THRESHOLD = 50; // 50% quorum required to approve a proposal
    uint256 public constant VOTING_REWARD = 1 * 10 ** uint256(decimals); // 1 GMC reward for voting 

    // Vesting Schedules
    uint256 public constant TEAM_VESTING_PERIOD = 2 years;
    uint256 public constant TEAM_CLIFF_PERIOD = 6 months;
    uint256 public constant INVESTOR_VESTING_PERIOD = 1 year;
    uint256 public constant INVESTOR_RELEASE_PERIOD = 3 months; 

    // Governance Variables
    uint256 public proposalCount;
    uint256 public nextProposalId;
    uint256 public proposalThreshold = MIN_PROPOSAL_THRESHOLD;
    address public governor;
    mapping(uint256 => Proposal) public proposals; 

    struct Proposal {
        uint256 id;
        address proposer;
        string title;
        string description;
        uint256 startBlock;
        uint256 endBlock;
        uint256 forVotes;
        uint256 againstVotes;
        mapping(address => bool) voted;
        mapping(address => uint256) votedProposal;
        bool executed;
    } 

    // Constructor
    constructor(uint256 _totalSupply) {
        totalSupply = _totalSupply * 10 ** uint256(decimals);
        balanceOf[msg.sender] = totalSupply;
        governor = msg.sender;
        nextProposalId = 1;
    } 

    // ERC20 Token
function transfer(address _to, uint256 _value) public returns (bool success) {
    require(balanceOf[msg.sender] >= _value, "Insufficient balance");
    balanceOf[msg.sender] -= _value;
    balanceOf[_to] += _value;
    emit Transfer(msg.sender, _to, _value);
    return true;
} 

function approve(address _spender, uint256 _value) public returns (bool success) {
    allowance[msg.sender][_spender] = _value;
    emit Approval(msg.sender, _spender, _value);
    return true;
} 

function transferFrom(address _from, address _to, uint256 _value) public returns (bool success) {
    require(balanceOf[_from] >= _value, "Insufficient balance");
    require(allowance[_from][msg.sender] >= _value, "Allowance exceeded");
    balanceOf[_from] -= _value;
    balanceOf[_to] += _value;
    allowance[_from][msg.sender] -= _value;
    emit Transfer(_from, _to, _value);
    return true;
} 

// Staking Functions
function stake(uint256 _amount) public {
    require(balanceOf[msg.sender] >= _amount, "Insufficient balance");
    require(_amount >= MIN_STAKE_AMOUNT, "Minimum stake amount not met");
    balanceOf[msg.sender] -= _amount;
    stakedBalance[msg.sender] += _amount;
    lastStakeTimestamp[msg.sender] = block.timestamp;
    emit Staked(msg.sender, _amount);
} 

function withdraw(uint256 _amount) public {
    require(stakedBalance[msg.sender] >= _amount, "Insufficient staked balance");
    require(block.timestamp >= lastStakeTimestamp[msg.sender] + STAKE_LOCK_PERIOD, "Stake locked");
    stakedBalance[msg.sender] -= _amount;
    balanceOf[msg.sender] += _amount;
    emit Withdrawn(msg.sender, _amount);
} 

function lockStake(uint256 _amount) public {
    require(stakedBalance[msg.sender] >= _amount, "Insufficient staked balance");
    lockedStakes[msg.sender] += _amount;
    stakedBalance[msg.sender] -= _amount;
    emit Locked(msg.sender, _amount);
} 

function unlockStake(uint256 _amount) public {
    require(lockedStakes[msg.sender] >= _amount, "Insufficient locked stake balance");
    lockedStakes[msg.sender] -= _amount;
    stakedBalance[msg.sender] += _amount;
    emit Unlocked(msg.sender, _amount);
} 

function claimRewards() public {
    uint256 unlockedStakeBalance = stakedBalance[msg.sender] - lockedStakes[msg.sender];
    uint256 reward = unlockedStakeBalance * REWARD_RATE * (block.timestamp - lastStakeTimestamp[msg.sender]) / REWARD_INTERVAL;
    contributionRewards[msg.sender] += reward;
    lastStakeTimestamp[msg.sender] = block.timestamp;
    emit ContributionReward(msg.sender, reward);
} 

function claimLiquidityRewards() public {
    uint256 reward = liquidityRewards[msg.sender];
    liquidityRewards[msg.sender] = 0;
    balanceOf[msg.sender] += reward;
    emit LiquidityReward(msg.sender, reward);
} 

// Governance Functions
function submitProposal(string memory _title, string memory _description) public returns (uint256 proposalId) {
    require(balanceOf[msg.sender] >= proposalThreshold, "Insufficient tokens to submit proposal");
    proposalId = nextProposalId;
    Proposal storage p = proposals[proposalId];
    p.id = proposalId;
    p.proposer = msg.sender;
       p.title = _title;
    p.description = _description;
    p.startBlock = block.number;
    p.endBlock = block.number + VOTING_PERIOD;
    nextProposalId++;
    emit Approval(msg.sender, address(this), proposalThreshold);
    return proposalId;
} 

function voteProposal(uint256 _proposalId, bool _support) public {
    Proposal storage p = proposals[_proposalId];
    require(balanceOf[msg.sender] >= 1, "Insufficient tokens to vote");
    require(!p.voted[msg.sender], "Already voted");
    require(block.number >= p.startBlock && block.number <= p.endBlock, "Voting period ended");
    if (_support) {
        p.forVotes += balanceOf[msg.sender];
    } else {
        p.againstVotes += balanceOf[msg.sender];
    }
    p.voted[msg.sender] = true;
    p.votedProposal[msg.sender] = _proposalId;
    emit Approval(msg.sender, address(this), VOTING_REWARD);
} 

function executeProposal(uint256 _proposalId) public {
    Proposal storage p = proposals[_proposalId];
    require(block.number > p.endBlock, "Voting period not ended");
    require(!p.executed, "Already executed");
    require(p.forVotes > p.againstVotes, "Proposal rejected");
    p.executed = true;
    (bool success,) = address(this).call(abi.encodeWithSignature(p.description));
    require(success, "Execution failed");
} 

function setProposalThreshold(uint256 _proposalThreshold) public {
    require(msg.sender == governor, "Only governor can set proposal threshold");
    proposalThreshold = _proposalThreshold;
} 

function setGovernor(address _governor) public {
    require(msg.sender == governor, "Only governor can set governor");
    governor = _governor;
} 

// Contribution Functions
function becomeGameDeveloper() public {
    isGameDeveloper[msg.sender] = true;
} 

function becomeBugReporter() public {
    isBugReporter[msg.sender] = true;
} 

function claimContributionRewards() public {
    uint256 reward = contributionRewards[msg.sender];
    contributionRewards[msg.sender] = 0;
    balanceOf[msg.sender] += reward;
    emit ContributionReward(msg.sender, reward);
} 

function claimLiquidityRewards() public {
    uint256 reward = liquidityRewards[msg.sender];
    liquidityRewards[msg.sender] = 0;
    balanceOf[msg.sender] += reward;
    emit LiquidityReward(msg.sender, reward);
} 

// Vesting Functions
function releaseTeamTokens(address _teamMember) public {
    require(msg.sender == governor, "Only governor can release team tokens");
    require(block.timestamp >= lastStakeTimestamp[_teamMember] + TEAM_CLIFF_PERIOD, "Team member still in cliff period");
    uint256 releaseAmount = balanceOf[_teamMember] / (TEAM_VESTING_PERIOD / REWARD_INTERVAL);
    balanceOf[_teamMember] -= releaseAmount;
    balanceOf[governor] += releaseAmount;
} 

function releaseInvestorTokens(address _investor) public {
    require(msg.sender == governor, "Only governor can release investor tokens");
    require(block.timestamp >= lastStakeTimestamp[_investor] + INVESTOR_RELEASE_PERIOD, "Investor tokens still locked");
    uint256 releaseAmount = balanceOf[_investor] / (INVESTOR_VESTING_PERIOD / REWARD_INTERVAL);
    balanceOf[_investor] -= releaseAmount;
    balanceOf[governor] += releaseAmount;
}
}
