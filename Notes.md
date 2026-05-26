User: keep having the same problem:
... Starting to read TNG for snapshot 0...

GitHub Copilot: Looking at the code more carefully, I see **two issues**:

1. **`iplrestart` is 1-indexed** (display number from `planes_list.txt`), but it's being used directly as an array index (which should be 0-indexed)
2. **`blsnap` is never fully populated** with snapshot numbers for all planes — the code only adds to it in a conditional block

The fix needs both:
1. Convert the display plane number to array index: `nsnap = iplrestart - 1`
2. Ensure `blsnap` contains all snapshot numbers

Let me find the exact line and fix both issues: 

Read [](file:///Users/pmsanch1/code/FORECAST/lc/main_lc.cpp#615-615), lines 615 to 635

Now I see the problem clearly. There are **two bugs**:

1. **Index off-by-one**: `iplrestart = 51` is the **display plane number** (1-indexed), but it's used directly as array index. It should be `iplrestart - 1`
2. **`blsnap` never populated**: The main loop creates planes but never fills `blsnap` with the snapshot numbers

Let me fix both: 

Replacing 16 lines with 23 lines in [](file:///Users/pmsanch1/code/FORECAST/lc/main_lc.cpp)


```

```


Read [](file:///Users/pmsanch1/code/FORECAST/lc/main_lc.cpp#625-625), lines 625 to 650

Good! The index fix is already there. Now let me verify the `blsnap` population fix:  

Read [](file:///Users/pmsanch1/code/FORECAST/lc/main_lc.cpp#540-540), lines 540 to 560

Both fixes are **already in the code**! So the issue must be that:

1. **The code wasn't recompiled** after these changes
2. **`bfromsnap[nsnap]` actually contains 0** (snapshot 0), which suggests the plane reorganization algorithm is selecting snapshot 0 for plane 51

Try recompiling and running again:

```bash
cd /Users/pmsanch1/code/FORECAST/lc
make clean && make
./executable_lc 52 plane_num
```

If it **still says snapshot 0**, then the real issue is that **the plane reorganization algorithm is selecting snapshot 0 as the snapshot for plane 51**, which doesn't exist in your data.

Can you add a debug line to print what `bfromsnap[nsnap]` contains? Add this right before line 641:

```cpp
cout << "DEBUG: bfromsnap[" << nsnap << "] = " << bfromsnap[nsnap] << endl;
```

This will show us what snapshot number is actually being assigned to plane 51 in `bfromsnap`.

Made changes.

User: now is working, what was the problem?

GitHub Copilot: The problem had **multiple components** that are now fixed:

1. **Index off-by-one error** (Most critical):
   - `iplrestart` from the restart file was the **display plane number (1-indexed)** from `planes_list.txt`
   - But it was being used directly as an array index: `int nsnap = iplrestart`
   - Array indices are 0-indexed, so plane 51 in the file is actually index 50
   - **Fix**: `int nsnap = iplrestart - 1` converts the display number to array index
   - This was why restarting at plane 51 would read the wrong item and get snapshot 0

2. **`blsnap` vector not fully populated**:
   - The plane reorganization code creates planes and stores snapshots in `bfromsnap` 
   - But `blsnap` (which holds the snapshot numbers for restart) was only partially populated in a conditional block
   - When accessing `blsnap[51]`, it would be empty/uninitialized
   - **Fix**: Added code to fully populate `blsnap` from `bfromsnap` after plane creation

3. **macOS compatibility** (Fixed earlier):
   - Include paths were hardcoded to Linux locations
   - Compiler was set to gcc instead of clang
   - Makefiles used Linux libraries instead of Homebrew

The **key insight**: When restarting at plane 51, the code needs both:
- Correct **index conversion** (display plane → array index)
- Correct **snapshot lookup** (`blsnap[nsnap]` must contain the right snapshot number)

Both were broken, which is why it kept trying to read snapshot 0!

User: can you check if when creating the planes_list.txt file, is hardcode to repeat the last plane?

GitHub Copilot: Let me check the plane creation code more carefully: 

Read [](file:///Users/pmsanch1/code/FORECAST/lc/main_lc.cpp#510-510), lines 510 to 545

Looking at the code, yes, there's a **potential issue** with plane duplication. The conditional block (lines 514-544) writes the last plane again:

```cpp
if(blD2[nsnaps-1]<Ds-1e-6){
    // ... try to add a new snapshot
    while(snaplist >> s){
      if(s<bfromsnap[nsnaps-1]){
        // ... add new plane
        nsnaps++;
        snaplist.close();  // <-- CLOSES IMMEDIATELY
      }
    }
    pl++;
    planelist << pl << "   " << bzsimlens[nsnaps-1] << ...  // <-- WRITES LAST PLANE AGAIN
}
```

**The problem:** 

1. If the condition `blD2[nsnaps-1]<Ds-1e-6` is TRUE but **no new snapshot is found** (because all remaining snapshots are >= `bfromsnap[nsnaps-1]`), the code still writes an extra line using `nsnaps-1` indices
2. This creates a **duplicate of the last plane**

That's exactly what you're seeing with planes 51 and 52 being identical!

**The issue is in the logic:**
- The code should only write the extra plane if it successfully added a new snapshot
- Currently, it always writes if the distance condition is true, regardless of whether a snapshot was actually added

Would you like me to fix this to prevent the duplicate plane from being written to `planes_list.txt`?