import urllib.parse

dot1 = """digraph G {
    rankdir=LR;
    node [shape=box, style=filled, fillcolor=lightgrey, fontname="Arial"];
    
    subgraph cluster_orchestrator {
        label="Orchestrator (Heal Action)"; color=blue;
        create_job [label="Create Cloud Batch Job\njob_id: 'batch_2'\nBENCHHUB_RUN_ID: 'run_x'\nRESUME_FROM: 'run_x'", fillcolor=lightblue];
    }
    subgraph cluster_worker {
        label="Worker (batch_2)"; color=orange;
        download [label="Download gs://.../run_x/raw_logs.zip", fillcolor=moccasin];
        resume [label="harbor jobs resume", fillcolor=moccasin];
        upload [label="Upload to gs://.../run_x/raw_logs.zip", fillcolor=moccasin];
    }
    create_job -> download [label=" Start Worker"];
    download -> resume;
    resume -> upload;
}"""

dot2 = """digraph G {
    rankdir=TB;
    node [shape=note, style=filled, fillcolor=lightyellow, fontname="Arial"];
    
    subgraph cluster_bq {
        label="BigQuery Changes (1:MANY relationship)"; color=green;
        jobs_table [label="eval_results_jobs\nRow 1: (run_x, batch_1, 40/80)\nRow 2: (run_x, batch_2, 80/80)", shape=cylinder, fillcolor=lightgreen];
        
        get_job [label="get_job()\nSELECT * FROM jobs_table\nWHERE run_id = @run_id\nORDER BY updated_at DESC LIMIT 1", fillcolor=lightcyan];
        list_jobs [label="list_jobs()\nSELECT * FROM (\nSELECT *, ROW_NUMBER() OVER(\nPARTITION BY run_id ORDER BY updated_at DESC) as rn\nFROM jobs_table) WHERE rn=1", fillcolor=lightcyan];
    }
    
    jobs_table -> get_job [label=" Returns Row 2"];
    jobs_table -> list_jobs [label=" Returns Row 2"];
}"""

print("URL1:", f"https://quickchart.io/graphviz?graph={urllib.parse.quote(dot1)}")
print("URL2:", f"https://quickchart.io/graphviz?graph={urllib.parse.quote(dot2)}")
