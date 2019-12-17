export const MCUs = [
    { value: 'arduino', label: 'Arduino', stock: 5 },
    { value: 'launchPad', label: 'LaunchPad', stock: 69},
    { value: 'nodeMCU', label: 'NodeMCU', stock: 6 },
    { value: 'photonBoard', label: 'Photon Board', stock: 50 },
    { value: 'raspberryPi', label: 'Raspberry Pi', stock: 21 },
    { value: 'electron', label: 'The Electron', stock: 1 },
    { value: 'green', label: 'Green', stock: 9 },
];
  
export const shields = [
    { value: 'avr', label: 'AVR', stock: 5 },
    { value: 'bluetoothModule', label: 'Bluetooth Wireless Module', stock: 29 },
    { value: 'controllerShield', label: 'Controller Shield', stock: 5 },
    { value: 'gyroscope', label: 'Gyroscope', stock: 5 },
];

export const teams = [
    { value: 'team1', label: 'Team 1' },
    { value: 'team2', label: 'Team 2' },
    { value: 'team3', label: 'Team 3' },
    { value: 'team4', label: 'Team 4' },
    
]

export let quantity = [];
for (let i = 1; i < 16; i++) {
    quantity = quantity.concat({value: i, label: i});
} 

export const groupedOptions = [
    {
        label: 'MCUs',
        options: MCUs,
      },
      {
        label: 'Shields and Breakout Boards',
        options: shields,
      },
      {
        label: 'Sensors',
        options: shields,
      },
      {
        label: 'Computer Peripherals',
        options: shields,
      },
      {
        label: 'Acuators and speakers',
        options: shields,
      },
      {
        label: 'Power Supply',
        options: shields,
      },
      {
        label: 'Passive',
        options: shields,
      },
      {
        label: 'Mechanical',
        options: shields,
      },
];

// export default quantity;
