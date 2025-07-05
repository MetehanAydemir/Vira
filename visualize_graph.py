# Derlenmiş LangGraph uygulamasını içe aktar
from vira.graph.build import app

def create_diagram():
    """
    LangGraph uygulamasının bir Mermaid PNG diyagramını oluşturur.
    """
    try:
        # Grafiğin bir resmini çiz ve kaydet
        app.get_graph().draw_mermaid_png(
            output_file_path="vira_workflow_diagram.png",
        )
        print("Graf diyagramı 'vira_workflow_diagram.png' olarak başarıyla oluşturuldu!")
    except Exception as e:
        print(f"Diyagram oluşturulurken bir hata oluştu: {e}")
        print("Not: Bu özellik için 'pygraphviz' ve 'Graphviz' sisteminize kurulmuş olmalıdır.")

if __name__ == "__main__":
    create_diagram()