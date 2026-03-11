import urllib.parse

dot = """digraph G {
    rankdir=LR;
    node [shape=box, style=filled, fillcolor=lightgrey, fontname="Arial"];
    
    subgraph cluster_runs {
        label = "Bench-Hub Heal Sequence";
        style = dashed;
        color = blue;
        
        run_x [label="Original Run\n(run_x)\n40/80 completed", fillcolor=salmon];
        run_x_heal123 [label="Heal Run 1\n(run_x_heal_123)\n60/80 completed", fillcolor=lightgoldenrod];
        run_x_heal124 [label="Heal Run 2\n(run_x_heal_124)\n75/80 completed", fillcolor=lightgreen];
        
        run_x -> run_x_heal123 [label=" RESUME_FROM=run_x "];
        run_x_heal123 -> run_x_heal124 [label=" RESUME_FROM=run_x_heal_123 "];
    }
    
    subgraph cluster_gcs {
        label = "GCS Storage (Same Bucket, New Prefixes)";
        style = dashed;
        color = orange;
        
        gcs_x [label="gs://bucket/run_x/\nraw_logs.zip", shape=cylinder, fillcolor=lightblue];
        gcs_h1 [label="gs://bucket/run_x_heal_123/\nraw_logs.zip", shape=cylinder, fillcolor=lightblue];
        gcs_h2 [label="gs://bucket/run_x_heal_124/\nraw_logs.zip", shape=cylinder, fillcolor=lightblue];
    }
    
    run_x -> gcs_x [label=" Uploads", style=dotted];
    gcs_x -> run_x_heal123 [label=" Downloads", style=dotted];
    run_x_heal123 -> gcs_h1 [label=" Uploads merged", style=dotted];
    gcs_h1 -> run_x_heal124 [label=" Downloads", style=dotted];
    run_x_heal124 -> gcs_h2 [label=" Uploads merged", style=dotted];
}"""

encoded = urllib.parse.quote(dot)
url = f"https://quickchart.io/graphviz?graph={encoded}"
print(url)
