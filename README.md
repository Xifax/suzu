鈴 (suzu - bell)
Nonstop Spaced Repetition utility, implemented with python and pyside.

---

Requirements:

* Python (preferably 2.6.6)
* PySide (1.0.0 or greater)
* MeCab binaries

Install:

	python install.py

Launch:

	python suzu.py
	python suzuw.pyw

Notes:

* As of now uromkan may not convert romaji to kana (IME input still possible)
* Automatic dictionaries download/conversion does not works
* There may be some inaccuracies in how mecab parses example sentences
* Config .ini stores japanese characters, which may result in some minor glitches
* Some options currently do not work
* It's recommended to use plastique theme
* For now, only kanji mode is supported

Resources (as of now, somewhat in disarray):

* krad, edict, kanjidic from cjktools-data		/context help
* jmdict, kanjidic2 in sqlite					/jlpt levels, grades and frequency
* pickled jmdict								/fast search in popup dictionary
* pickled Kanji.Odyssey groups					/similar kanji
* kanjikafe stroke order diagramms				/stroke order