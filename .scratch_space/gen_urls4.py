import urllib.parse

dot_arch = """digraph G {
    rankdir=LR;
    node [shape=note, style=filled, fillcolor=lightyellow, fontname="Arial"];
    
    subgraph cluster_bq {
        label="BigQuery Schema Change: 1:MANY Relationship"; color=green;
        jobs_table [label="eval_results_jobs\nRow 1: (run_x, batch_1, 40/80)\nRow 2: (run_x, batch_2, 80/80)", shape=cylinder, fillcolor=lightgreen];
        
        get_job [label="get_job()\nSELECT * FROM jobs_table\nWHERE run_id = @run_id\nORDER BY updated_at DESC LIMIT 1", fillcolor=lightcyan];
        list_jobs [label="list_jobs()\nSELECT * FROM (\nSELECT *, ROW_NUMBER() OVER(\nPARTITION BY run_id ORDER BY updated_at DESC) as rn\nFROM jobs_table) WHERE rn=1", fillcolor=lightcyan];
    }
    
    jobs_table -> get_job [label=" Returns Row 2"];
    jobs_table -> list_jobs [label=" Returns Row 2"];
}"""

print("URL_ARCH:", f"https://quickchart.io/graphviz?graph={urllib.parse.quote(dot_arch)}")
