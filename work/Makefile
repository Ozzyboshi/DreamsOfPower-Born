# Dreams of Power - Born
#
#   make          -> dreams (AmigaDOS executable) + dreams.adf
#   make verify   -> checks that dreams.asm still gives back the original program
#   make assets   -> extracts graphics, music and texts into assets/
#   make run      -> FS-UAE, A500, KS 1.3, 512K chip + 512K slow
#   make run600   -> FS-UAE, A600, KS 2.05, 1MB chip (stock)
#   make run1200  -> FS-UAE, A1200, KS 3.1, 2MB chip, no fast RAM
#   make clean

VASM      ?= vasmm68k_mot
EXE2ADF   ?= exe2adf
FSUAE     ?= fs-uae
PYTHON    ?= python3
KSDIR     ?= $(HOME)/Documenti/FS-UAE/Kickstarts
KICKSTART ?= $(KSDIR)/Kickstart v1.3 rev 34.5 (1987)(Commodore)(A500-A1000-A2000-CDTV)[!].rom
KICK600   ?= $(KSDIR)/Kickstart v2.05 rev 37.299 (1991)(Commodore)(A600)[!].rom
KICK1200  ?= $(KSDIR)/Kickstart v3.1 rev 40.68 (1993)(Commodore)(A1200).rom

# -no-opt keeps every instruction as written (same size and timing)
VASMFLAGS = -m68000 -Fhunkexe -kick1hunks -nosym -no-opt -quiet

all: dreams dreams.adf

dreams: dreams.asm data_55000.bin
	$(VASM) $(VASMFLAGS) -o $@ $<

dreams.adf: dreams
	$(EXE2ADF) -i $< -a $@ -l DREAMS

# the inner executable and the block it unpacks to $55000
dreams_unpacked data_55000.bin: ../DreamsOfPower-Born
	$(PYTHON) decrunch.py "$<" dreams_unpacked data_55000.bin

# 1) ORIGINAL build at 0 must be identical to the code hunk of the program
# 2) the same build moved by $100000 must differ only where an address is
verify: dreams_unpacked
	$(PYTHON) hunkdata.py dreams_unpacked hunk0.bin
	$(VASM) -m68000 -Fbin -no-opt -quiet -DORIGINAL -o orig_0.bin dreams.asm
	cmp orig_0.bin hunk0.bin && echo "ORIGINAL build: identical to the original code hunk"
	$(VASM) -m68000 -Fbin -no-opt -quiet -DORIGINAL -DMOVED -o orig_100000.bin dreams.asm
	$(PYTHON) checkreloc.py orig_0.bin orig_100000.bin dreams.asm
	rm -f hunk0.bin orig_0.bin orig_100000.bin

assets: data_55000.bin dreams_unpacked
	$(PYTHON) extract_assets.py dreams_unpacked data_55000.bin assets

run: dreams.adf
	$(FSUAE) --amiga_model=A500 \
		--kickstart_file="$(KICKSTART)" \
		--chip_memory=512 --slow_memory=512 --fast_memory=0 \
		--floppy_drive_0="$(abspath dreams.adf)" \
		--floppy_drive_speed=0

run600: dreams.adf
	$(FSUAE) --amiga_model=A600 \
		--kickstart_file="$(KICK600)" \
		--chip_memory=1024 --slow_memory=0 --fast_memory=0 \
		--floppy_drive_0="$(abspath dreams.adf)" \
		--floppy_drive_speed=0

run1200: dreams.adf
	$(FSUAE) --amiga_model=A1200 \
		--kickstart_file="$(KICK1200)" \
		--chip_memory=2048 --fast_memory=0 \
		--floppy_drive_0="$(abspath dreams.adf)" \
		--floppy_drive_speed=0

clean:
	rm -f dreams dreams.adf hunk0.bin orig_0.bin orig_100000.bin

.PHONY: all verify assets run run600 run1200 clean
