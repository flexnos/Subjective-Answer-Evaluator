"""
Generate Sample PDFs for Testing Answer Sheet Evaluation
Run this script to create 3 test PDFs: Question Paper, Reference Answers, Student Answer Sheet
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from datetime import datetime

def create_question_paper():
    """Generate Question Paper PDF"""
    filename = "sample_question_paper.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='darkblue',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Question style
    question_style = ParagraphStyle(
        'Question',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=20,
        leftIndent=20
    )
    
    # Header
    story.append(Paragraph("SAMPLE EXAMINATION", title_style))
    story.append(Paragraph("Mid-Term Biology Test", styles['Heading2']))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Paragraph("Total Marks: 50 | Time: 2 Hours", styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    
    # Questions
    questions = [
        ("Q1. What is photosynthesis? Explain the process in detail.", 10),
        ("Q2. Describe the structure and function of mitochondria.", 10),
        ("Q3. Explain the process of cellular respiration and its importance.", 15),
        ("Q4. What are enzymes? Discuss their role in biological reactions.", 10),
        ("Q5. Describe the structure of DNA and its significance in heredity.", 5)
    ]
    
    story.append(Paragraph("<b>Instructions:</b> Answer all questions. Write clearly.", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    for q_text, marks in questions:
        story.append(Paragraph(f"<b>{q_text}</b> <i>[{marks} marks]</i>", question_style))
        story.append(Spacer(1, 0.2*inch))
    
    doc.build(story)
    print(f"✅ Created: {filename}")

def create_reference_answers():
    """Generate Reference Answers PDF"""
    filename = "sample_reference_answers.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor='darkgreen',
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    answer_style = ParagraphStyle(
        'Answer',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=15,
        leftIndent=20
    )
    
    # Header
    story.append(Paragraph("REFERENCE ANSWERS - MARKING SCHEME", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Reference answers
    answers = [
        ("Q1", """Photosynthesis is the process by which green plants use sunlight, water, and carbon dioxide to produce oxygen and glucose. It occurs in chloroplasts and involves two main stages: light-dependent reactions (light reactions) and light-independent reactions (Calvin cycle). During light reactions, chlorophyll absorbs sunlight and splits water molecules, releasing oxygen. The energy captured is used to produce ATP and NADPH. In the Calvin cycle, CO2 is fixed and converted into glucose using the energy from ATP and NADPH. This process is essential for life on Earth as it produces oxygen and organic compounds."""),
        
        ("Q2", """Mitochondria are double-membrane organelles known as the powerhouse of the cell. The outer membrane is smooth, while the inner membrane is highly folded into cristae, which increase surface area for ATP production. The space inside is called the matrix, containing enzymes for the Krebs cycle. Mitochondria generate ATP through cellular respiration, particularly oxidative phosphorylation. They also play roles in calcium signaling, cell death regulation, and metabolic pathways. Mitochondria have their own DNA and ribosomes, suggesting they evolved from ancient bacteria."""),
        
        ("Q3", """Cellular respiration is the process by which cells break down glucose to produce ATP (energy). It occurs in three main stages: glycolysis (in cytoplasm), Krebs cycle (in mitochondrial matrix), and electron transport chain (on inner mitochondrial membrane). Glycolysis breaks glucose into pyruvate, producing 2 ATP. The Krebs cycle oxidizes acetyl-CoA, releasing CO2 and generating NADH and FADH2. The electron transport chain uses these molecules to create a proton gradient that drives ATP synthesis, producing approximately 32-34 ATP per glucose molecule. This process is crucial for providing energy for all cellular activities."""),
        
        ("Q4", """Enzymes are biological catalysts that speed up chemical reactions without being consumed. They are primarily proteins with specific three-dimensional structures that form active sites. Enzymes lower the activation energy required for reactions, allowing them to occur at body temperature. They are highly specific, following the lock-and-key or induced-fit model. Enzyme activity is affected by temperature, pH, substrate concentration, and inhibitors. They play vital roles in digestion, metabolism, DNA replication, and virtually all biochemical processes in living organisms."""),
        
        ("Q5", """DNA (deoxyribonucleic acid) is a double-helix molecule consisting of two complementary strands. Each strand is made of nucleotides containing a sugar (deoxyribose), phosphate group, and one of four nitrogenous bases: adenine (A), thymine (T), guanine (G), or cytosine (C). A pairs with T, and G pairs with C through hydrogen bonds. DNA stores genetic information in the sequence of bases, which codes for proteins. It is the hereditary material passed from parents to offspring, ensuring traits are inherited. DNA replication ensures genetic continuity during cell division.""")
    ]
    
    for q_num, answer in answers:
        story.append(Paragraph(f"<b>{q_num}:</b>", styles['Heading3']))
        story.append(Paragraph(answer, answer_style))
        story.append(Spacer(1, 0.2*inch))
    
    doc.build(story)
    print(f"✅ Created: {filename}")

def create_student_answer_sheet():
    """Generate Student Answer Sheet PDF"""
    filename = "sample_student_answers.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor='darkred',
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    answer_style = ParagraphStyle(
        'Answer',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=15,
        leftIndent=20
    )
    
    # Header
    story.append(Paragraph("STUDENT ANSWER SHEET", title_style))
    story.append(Paragraph("Student Name: John Doe", styles['Normal']))
    story.append(Paragraph("Roll Number: 2024-BIO-001", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Student answers (varying quality)
    student_answers = [
        ("Q1", """Photosynthesis is how plants make food using sunlight. They take in carbon dioxide and water, and use chlorophyll in their leaves to convert these into glucose and oxygen. The process has two stages: light reactions that capture energy from sunlight, and dark reactions (Calvin cycle) that make glucose. Chlorophyll absorbs light and splits water molecules. The energy is used to produce ATP which is then used to convert CO2 into sugar. This process is important because it produces oxygen for us to breathe."""),
        
        ("Q2", """Mitochondria are the powerhouse of the cell. They have two membranes - outer and inner. The inner membrane has folds called cristae. Inside is the matrix which has enzymes. Mitochondria make ATP energy through respiration. They have their own DNA which suggests they came from bacteria long ago. They are very important for the cell's energy needs."""),
        
        ("Q3", """Cellular respiration breaks down glucose to make ATP energy. It happens in three steps. First is glycolysis which breaks glucose in the cytoplasm and makes some ATP. Then Krebs cycle happens in mitochondria and releases CO2. Last is the electron transport chain which makes lots of ATP. Overall about 36-38 ATP molecules are made from one glucose. This energy is needed for cell activities like growth and movement."""),
        
        ("Q4", """Enzymes are proteins that speed up reactions in the body. They have active sites where substrates bind. They lower activation energy so reactions can happen faster. Different enzymes work at different pH and temperature. Some enzymes break down food in digestion. Others help in metabolism. Without enzymes, reactions would be too slow to support life."""),
        
        ("Q5", """DNA is genetic material that carries hereditary information. It has a double helix shape with two strands. The strands have nucleotides with bases A, T, G, C. A pairs with T and G pairs with C. DNA stores information in the sequence of bases.""")
    ]
    
    for q_num, answer in student_answers:
        story.append(Paragraph(f"<b>{q_num}:</b>", styles['Heading3']))
        story.append(Paragraph(answer, answer_style))
        story.append(Spacer(1, 0.2*inch))
    
    doc.build(story)
    print(f"✅ Created: {filename}")

if __name__ == "__main__":
    print("📄 Generating Sample PDF Files for Testing...")
    print("-" * 50)
    
    try:
        create_question_paper()
        create_reference_answers()
        create_student_answer_sheet()
        
        print("-" * 50)
        print("✅ All sample PDFs created successfully!")
        print("\n📋 Files created:")
        print("  1. sample_question_paper.pdf")
        print("  2. sample_reference_answers.pdf")
        print("  3. sample_student_answers.pdf")
        print("\n🚀 Upload these files in your Streamlit app to test the PDF evaluation feature!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n⚠️  Make sure you have reportlab installed:")
        print("   pip install reportlab")