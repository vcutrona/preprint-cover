import sys
import os
import bibtexparser
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from reportlab.lib import colors

def parse_bib_file(bib_path):
    with open(bib_path, "r", encoding="utf-8") as bibfile:
        bib_content = bibfile.read()
        bibfile.seek(0)
        bib_database = bibtexparser.load(bibfile)
    
    entry = bib_database.entries[0]  # Assuming one entry per file
    
    title = entry.get("title", "Unknown Title")
    authors = entry.get("author", "Unknown Authors").replace("\n", " ")
    year = entry.get("year", "Unknown Year")
    journal = entry.get("journal", entry.get("booktitle", "Unknown Journal/Conference"))
    volume = entry.get("volume", "")
    issue = entry.get("number", "")
    pages = entry.get("pages", "")
    publisher = entry.get("publisher", "")
    doi = entry.get("doi", "")
    url = entry.get("url", "")
    arxiv_id = entry.get("eprint", "") if "arxiv" in entry.get("archiveprefix", "").lower() else ""
    abstract = entry.get("abstract", "")
    editors = entry.get("editor", "").replace("\n", " ")
    institution = entry.get("institution", "")
    series = entry.get("series", "")
    
    link = doi if doi else url
    if not link:
        link = input("No DOI or URL found in the .bib file. Please enter a DOI: ")
        if link:
            link = f"https://doi.org/{link.strip()}"
    print(authors, editors)
    return title, authors, year, journal, volume, issue, pages, publisher, link, arxiv_id, abstract, editors, institution, series, bib_content

def update_y_position(y, offset, height, top_margin, bottom_margin, canvas):
    new_y = y - offset
    if new_y < bottom_margin:  # New page if not enough space
        canvas.showPage()
        new_y = height - top_margin
    return new_y

def create_pdf_cover(title, authors, year, journal, volume, issue, pages, publisher, link, arxiv_id, abstract, editors, institution, series, bib_content, output_path):
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4
    left_margin = 50
    right_margin = 50
    top_margin = 50
    bottom_margin = 50
    y_position = height - top_margin
    
    # Add logo
    logo_file = input("Please enter a path to a logo (press ENTER to skip): ")
    if logo_file:
        logo_width = 100
        logo_height = 50
        logo_x = width - right_margin - logo_width
        logo_y = height - top_margin - logo_height
        c.drawImage(logo_file, logo_x, logo_y, width=logo_width, height=logo_height, preserveAspectRatio=True)
    
    y_position = update_y_position(y_position, 20, height, top_margin, bottom_margin, c)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(left_margin, y_position, "Preprint Version")
    y_position = update_y_position(y_position, 30, height, top_margin, bottom_margin, c)
    c.setFont("Helvetica", 12)
    c.drawString(left_margin, y_position, "This is a preprint version of the following publication:")
    y_position = update_y_position(y_position, 30, height, top_margin, bottom_margin, c)

    # Title
    c.setFont("Helvetica-Bold", 16)
    title_lines = simpleSplit(title, "Helvetica-Bold", 16, width - left_margin - right_margin)
    for line in title_lines:
        c.drawString(left_margin, y_position, line)
        y_position = update_y_position(y_position, 20, height, top_margin, bottom_margin, c)
    
    # Authors
    c.setFont("Helvetica", 12)
    authors_lines = simpleSplit(f"Authors: {authors}", "Helvetica", 12, width - left_margin - right_margin)
    for line in authors_lines:
        c.drawString(left_margin, y_position, line)
        y_position = update_y_position(y_position, 15, height, top_margin, bottom_margin, c)
    
    # Year, Journal/Conference, Volume, Issue, Pages
    y_position = update_y_position(y_position, 5, height, top_margin, bottom_margin, c)
    
    c.drawString(left_margin, y_position, f"Published in: {journal} ({year})")
    y_position = update_y_position(y_position, 20, height, top_margin, bottom_margin, c)
    if volume and issue:
        c.drawString(left_margin, y_position, f"Volume: {volume}, Issue: {issue}")
        y_position = update_y_position(y_position, 20, height, top_margin, bottom_margin, c)
    if pages:
        c.drawString(left_margin, y_position, f"Pages: {pages}")
        y_position = update_y_position(y_position, 20, height, top_margin, bottom_margin, c)
    if publisher:
        c.drawString(left_margin, y_position, f"Publisher: {publisher}")
        y_position = update_y_position(y_position, 20, height, top_margin, bottom_margin, c)
    if editors:
        editors = " ".join(simpleSplit(editors, "Helvetica", 12, width - 100))
        c.drawString(left_margin, y_position, f"Edited by: {editors}")
        y_position = update_y_position(y_position, 20, height, top_margin, bottom_margin, c)
    if institution:
        c.drawString(left_margin, y_position, f"Institution: {institution}")
        y_position = update_y_position(y_position, 20, height, top_margin, bottom_margin, c)
    if series:
        c.drawString(left_margin, y_position, f"Series: {series}")
        y_position = update_y_position(y_position, 20, height, top_margin, bottom_margin, c)
    
    # DOI or URL
    if link:
        c.setFont("Helvetica-Oblique", 12)
        c.drawString(left_margin, y_position, "Official version available at: ")
        c.setFillColor(colors.blue)
        c.linkURL(link, (left_margin + 150, y_position, 500, y_position + 12), relative=0)
        c.drawString(left_margin + 150, y_position, link)
        c.setFillColor(colors.black)
        y_position = update_y_position(y_position, 20, height, top_margin, bottom_margin, c)
    
    # ArXiv ID
    if arxiv_id:
        c.setFont("Helvetica-Oblique", 12)
        c.drawString(left_margin, y_position, f"ArXiv ID: {arxiv_id}")
        y_position = update_y_position(y_position, 20, height, top_margin, bottom_margin, c)
    
    y_position = update_y_position(y_position, 5, height, top_margin, bottom_margin, c)
    
    # Abstract
    if abstract:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left_margin, y_position, "Abstract")
        y_position = update_y_position(y_position, 15, height, top_margin, bottom_margin, c)
        c.setFont("Helvetica", 10)
        abstract_lines = simpleSplit(abstract, "Helvetica", 10, width - 100)
        for line in abstract_lines:
            c.drawString(left_margin, y_position, line)
            y_position = update_y_position(y_position, 12, height, top_margin, bottom_margin, c)
    
    # BibTeX
    y_position = update_y_position(y_position, 13, height, top_margin, bottom_margin, c)
    c.setFont("Helvetica-Oblique", 12)
    c.drawString(left_margin, y_position, "How to cite this work (.bib)")
    y_position = update_y_position(y_position, 15, height, top_margin, bottom_margin, c)
    c.setFont("Courier", 8)
    bib_lines = simpleSplit(bib_content, "Courier", 8, width - 100)
    for line in bib_lines:
        c.drawString(left_margin, y_position, line)
        y_position = update_y_position(y_position, 10, height, top_margin, bottom_margin, c)
    
    c.save()

def main():
    if len(sys.argv) < 2:
        print("Drag and drop a .bib file onto this script.")
        sys.exit(1)
    
    bib_path = sys.argv[1]
    if not os.path.exists(bib_path) or not bib_path.endswith(".bib"):
        print("Please provide a valid .bib file.")
        sys.exit(1)
    
    title, authors, year, journal, volume, issue, pages, publisher, link, arxiv_id, abstract, editor, institution, series, bib_content = parse_bib_file(bib_path)
    output_pdf = os.path.splitext(bib_path)[0] + "_preprint_cover.pdf"
    create_pdf_cover(title, authors, year, journal, volume, issue, pages, publisher, link, arxiv_id, abstract, editor, institution, series, bib_content, output_pdf)
    print(f"Preprint cover created: {output_pdf}")

if __name__ == "__main__":
    main()

