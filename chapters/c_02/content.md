# This Documentation System

The notes are very lean.

Each chapter is a self-contained markdown document, so you can preview it.

If you want to produce a PDF file with all chapters, a **build.py** Python program will add each chapter into a single book.

I'm establishing conventions so the goal of duality rendering, either stand-alone markdown or single PDF, is easier to achieve.

These are the rules:

1. Book title is set in **template.yaml**.
1. Chapters are stored in the **chapters** directory.
1. Each chapter is self-contained on a directory whose name is "c_nn", where "nn" is two digits.
1. The content of a chapter goes in the file **content.md**.
1. Do not use `# Chapter 3: My Chapter`, just use `# My Chapter`, the build process will automatically do numbering for you.
1. A directory **src** is for images sources like drawio or mermaid diagrams.
1. A directory **resources** are for png or jpg files.
1. If you want to change the chapter ordering, rename the directory, e.g. from c_10 to c_01 will make the tenth chapter, chapter number one.
1. There's no main document importing sub-documents. The build process dynamically add every chapter available in the directory **chapters**.

The **build.py** program follows the convention rules when processing each of the chapters, so numbering is good.

## Commands used to provide a building environment

In order to build PDF files, you'll need pandoc, LaTeX and Python installed.

```bash
brew install pandoc
brew install basictex
sudo tlmgr update --self
sudo tlmgr install titlesec
sudo tlmgr install xcolor
sudo tlmgr install fancyhdr
```
