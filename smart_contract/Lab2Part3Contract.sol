pragma solidity ^0.5.0;

contract Airlines{
    
    mapping (address => bool) registeredAirlines;
    address contractOwnerAddress = 0xE75D9DE667F7FFaCD7a300E02dc4e6654598cA77;
    uint priceToRegister = 0;
    
    modifier contractOwner(){
        require(
            msg.sender == contractOwnerAddress,
            "Only contract owner can call this."
        );
        _;
    }
    
    modifier registered(){
        require(
            registeredAirlines[msg.sender] == true,
            "Only registered airlines can call this."
        );
        _;
    }
    
    modifier costs(uint price) {
        if (msg.value >= price) {
            _;
        }
    }
    
    function register() public payable costs(priceToRegister){
        registeredAirlines[msg.sender] = true;
    }
    
    function request(address toAirline, string memory details) public registered{
        emit Request(msg.sender, toAirline, details);
    }
    
    function response(address fromAirline, string memory details, bool successful) public registered {
        emit Response(msg.sender, fromAirline, details, successful);
        if(successful){
            settlePayment(fromAirline);
        }
    }
    
    function settlePayment(address toAirline) public registered {
        emit Payment(msg.sender, toAirline);
    }
    
    function unregister(address airline) public contractOwner {
        registeredAirlines[airline] = false;
    }
    
    function changeRegisterPrice(uint newPrice) public contractOwner {
        priceToRegister = newPrice;
    }
    
    event Request(address fromAirline, address toAirline, string details);
    event Response(address toAirline, address fromAirline, string details, bool successful);
    event Payment(address fromAirline, address toAirline);
    event Register(address airline);
}