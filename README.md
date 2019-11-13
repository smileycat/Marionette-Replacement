# Marionette Replacement

Replace the monkey in 'monkey.mov' with another character, and imitate the original motion by recognising red parts of the monkey.

## Concept

When looping through each frame of the video:

1. Generate a 2D map or a list of (x, y) coordinates containing the red pixels.

2. Apply segmentation algorithm to categorise the red pixels into 5 different body parts.

3. Replace the parts with simple shapes and connect with lines to form the character.

## Segmentation Algorithm

In this project, I was to design my own algorithm to solve the problem. There maybe other algorithms / laws existed that are fairly similar to mine since it's quite straightforward.

1. S = {S1, S2, ..., Sn}; where S is a list containing all Si sublists.
2. Add a pair of (x, y) red pixel coordinate to a new list S1.
3. For all the red pixels coordinates: If a red pixel is close enough (define a threshold k) to some avg(Si), then add the coord (x, y) to Si. Else add it into a new list Sn+1.

If the k value is appropriately chosen, the segmentation outcome should be fairly accurate.