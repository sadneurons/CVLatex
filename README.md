# Dr. Ross A. Dunne - Curriculum Vitae

This repository contains the LaTeX source for my academic CV, automatically compiled to both PDF and HTML.

## 📄 View CV

- **PDF Version**: [Download PDF](https://sadneurons.github.io/cv/cv.pdf)
- **HTML Version**: [View Online](https://sadneurons.github.io/cv/)

## 🔧 Local Compilation

### Prerequisites
- XeLaTeX (part of TeX Live or MacTeX)
- Biber (bibliography processor)
- Bembo font installed locally

### Build Commands
```bash
xelatex cv_dunne_jan_2026.tex
biber cv_dunne_jan_2026
xelatex cv_dunne_jan_2026.tex
xelatex cv_dunne_jan_2026.tex
```

Or simply save the file in VS Code with LaTeX Workshop extension installed.

## 🚀 Automatic Deployment

Every push to `main` triggers a GitHub Actions workflow that:
1. Compiles the PDF using XeLaTeX + Biber
2. Generates an HTML version using make4ht
3. Deploys both versions to GitHub Pages

## 📝 Structure

- `cv_dunne_jan_2026.tex` - Main CV file
- `my_publications.bib` - Publications bibliography
- `my_posters_abstracts.bib` - Conference presentations
- `bwphoto.png` - Profile photo
- `.github/workflows/build-cv.yml` - Automated build and deployment

## 🎨 Fonts

The local version uses Bembo. The GitHub Pages version falls back to TeX Gyre Pagella (similar serif font).

## 📧 Contact

Dr. Ross A. Dunne  
ross.dunne@gmmh.nhs.uk  
[ORCID](https://orcid.org/0000-0003-2046-6193) | [GitHub](https://github.com/sadneurons) | [LinkedIn](https://linkedin.com/in/ross-dunne-gmdrc)
