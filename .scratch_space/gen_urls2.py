import urllib.parse

dot1 = """digraph G {
    rankdir=TB;
    node [shape=box, style=filled, fillcolor=lightgrey, fontname="Arial"];
    subgraph cluster_orchestrator {
        label="Orchestrator (Heal Action)"; color=blue;
        create_job [label="Create Cloud Batch Job\njob_id: 'batch_2'\nBENCHHUB_RUN_ID: 'run_x'\nRESUME_FROM: 'run_x'", fillcolor=lightblue];
    }
    subgraph cluster_bq {
        label="BigQuery"; color=green;
        jobs_table [label="eval_results_jobs\nRow 1: (run_x, batch_1)\nRow 2: (run_x, batch_2)", shape=cylinder, fillcolor=lightgreen];
        instances_table [label="eval_results_instances\n(run_x, instance_1)\n(Overwritten by batch_2)", shape=cylinder, fillcolor=lightgreen];
    }
    subgraph cluster_worker {
        label="Worker (batch_2)"; color=orange;
        download [label="Download gs://.../run_x/raw_logs.zip", fillcolor=moccasin];
        resume [label="harbor jobs resume", fillcolor=moccasin];
        upload [label="Upload to gs://.../run_x/raw_logs.zip", fillcolor=moccasin];
    }
    create_job -> jobs_table [label=" Insert new row"];
    create_job -> download [label=" Start Worker"];
    download -> resume;
    resume -> upload;
    resume -> instances_table [label=" Upsert instances"];
    upload -> jobs_table [label=" Update Row 2 stats"];
}"""

dot2 = """digraph G {
    rankdir=LR;
    node [shape=note, style=filled, fillcolor=lightyellow, fontname="Arial"];
    old_merge [label="Current MERGE\nON T.run_id = S.run_id", fillcolor=lightcoral];
    new_merge [label="New MERGE\nON T.run_id = S.run_id\nAND T.job_id = S.job_id", fillcolor=lightgreen];
    old_update [label="Current UPDATE\nWHERE run_id = @run_id", fillcolor=lightcoral];
    new_update [label="New UPDATE\nWHERE run_id = @run_id\nAND job_id = @job_id", fillcolor=lightgreen];
    old_merge -> new_merge [label=" Allows multiple\njobs per run"];
    old_update -> new_update [label=" Updates only\nthe specific heal job"];
}"""

print("URL1:", f"https://quickchart.io/graphviz?graph={urllib.parse.quote(dot1)}")
print("URL2:", f"https://quickchart.io/graphviz?graph={urllib.parse.quote(dot2)}")
