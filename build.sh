#! /usr/bin/env bash

quarto render WebSlides
quarto render WebBook

mkdir -p _build/book/Figures/PDFs
cp -r WebBook/Figures/PDFs/*pdf _build/book/Figures/PDFs
