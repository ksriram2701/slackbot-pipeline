from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

def generate_pdf_report(filename, raw_keywords, cleaned_keywords, clusters, post_ideas, outlines):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    y = height - 50
    
    # Define margins
    left_margin = 50
    right_margin = width - 50
    max_width = right_margin - left_margin

    def write_section(title, content):
        nonlocal y
        
        # Write section title
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left_margin, y, title)
        y -= 20
        c.setFont("Helvetica", 12)

        # Convert content to text
        if isinstance(content, (list, tuple)):
            text = ", ".join(map(str, content))
        elif isinstance(content, dict):
            # Format key-value pairs nicely
            lines = [f"{k}: {v}" for k, v in content.items()]
            text = "\n".join(lines)
        else:
            text = str(content)

        # Process each line with proper wrapping
        for line in text.split("\n"):
            # Use reportlab's simpleSplit for proper text wrapping
            wrapped_lines = simpleSplit(line, "Helvetica", 12, max_width)
            
            for wrapped_line in wrapped_lines:
                # Check if we need a new page
                if y < 100:
                    c.showPage()
                    y = height - 50
                    c.setFont("Helvetica", 12)
                
                c.drawString(left_margin + 10, y, wrapped_line)
                y -= 15
        
        y -= 10  # Extra space after section

    # 1️⃣ Raw keywords
    write_section("Raw Keywords", raw_keywords)

    # 2️⃣ Cleaned keywords
    write_section("Cleaned Keywords", list(set(cleaned_keywords)))

    # 3️⃣ Cluster dictionary
    write_section("Cluster Dictionary", clusters)

    # 4️⃣ Outlines
    write_section("Outlines", outlines)

    # Optional: Post Ideas (if you want to keep them)
    write_section("Post Ideas", post_ideas)

    c.save()
    print(f"✅ PDF report saved as {filename}")