# Design Notes

Here I'd like to keep a list of notes for future designs.

## Version 3, Next Revision

These will be changes to the current major version, so basically small design tweaks using the same hardware

### Screen
- Show current design version on the screen
- Make temperatures bigger
- Perhaps make title headings smaller to allow for it

### Case
- Fix the lid mount posts, make them much taller in the base and reduce the towers on the lid accordingly
- Add screw relief in the lid so that the lid screws are within the plastic 
- Make sure to use proper wire strippers to get a great connection in the sensor breakout board
- Add small elevations to the bottom of the Pico so we only have to use 2 screws
- Use the power splitter jumper cable to eliminate the junction box
- Reduce the usb power hole slightly
- Perhaps just 2 screen screws
- Add about 0.25mm to each hole
- Document every screw used very carefully and decide whether we need larger holes or not
 - For sensor breakout board, I believe I currently used (2) M2.3x5
 - For Pico I believe I used (2) M2x6
 - For the lid, I believe I used (2) M2.3x8, but I am not sure

### Code
- Make the sensor box inherit the TFT and sensor base classes
- Try to clean it up as much as possible...simple simple

## Version 4

These are more drastic changes that necessitate another round of iteration, or different hardware.

### General
- Add a simple LED with a small hole in the case for it as a backup communication signal

### Screen
- I think start by trying a different screen, preferably one that doesn't have that drastic of a bezel exposed

### Case
- Consider using studs like a PC motherboard for the temperature sensor breakout board, and possibly the Pico
- But also on the Pico, consider just making a slot for it to slide in horizontally...it could reduce height
- Use a different connector for the sensors, perhaps a USB.  It really wouldn't be too hard to do this.  A nice USB C breakout board with a female port on the outside surface of the box (https://www.amazon.com/Female-Terminal-Adapter-Breakout-Output/dp/B0BKH21YGV/), and still use the sensor breakout board with the built-in resistor, and then just a screw terminal USB C male for the sensors to firmly screw into.

### Code
- Add unit testing
- Add script to auto clean up old results, run once a week and open a PR?
