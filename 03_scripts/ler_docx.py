import sys, docx, os
def read(p):
    d = docx.Document(p)
    out=[]
    for para in d.paragraphs:
        t=para.text.strip()
        if t: out.append(t)
    for ti,tb in enumerate(d.tables):
        out.append(f"\n[TABELA {ti+1}]")
        for row in tb.rows:
            out.append(" | ".join(c.text.strip() for c in row.cells))
    return "\n".join(out)
if __name__=="__main__":
    print(read(sys.argv[1]))
