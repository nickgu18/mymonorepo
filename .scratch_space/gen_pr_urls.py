import urllib.parse

# 1. Architecture Flow
dot_arch = """digraph G {
    rankdir=LR;
    fontname="Helvetica,Arial,sans-serif";
    node [fontname="Helvetica,Arial,sans-serif", style="filled,rounded", shape=box, fontcolor="#333333"];
    edge [fontname="Helvetica,Arial,sans-serif", color="#666666", penwidth=1.5];

    subgraph cluster_orchestrator {
        label="Orchestrator (Heal Action)";
        style=filled;
        color="#e3f2fd";
        pcolor="#bbdefb";
        fontcolor="#1565c0";
        fontsize=14;
        
        create_job [label=<<table border="0" cellborder="0" cellspacing="0">
            <tr><td align="center"><b>Create Cloud Batch Job</b></td></tr>
            <tr><td align="center"><font point-size="10">job_id: 'batch_2'</font></td></tr>
            <tr><td align="center"><font point-size="10">BENCHHUB_RUN_ID: 'run_x'</font></td></tr>
            <tr><td align="center"><font point-size="10">RESUME_FROM_RUN_ID: 'run_x'</font></td></tr>
        </table>>, fillcolor="#bbdefb", color="#1976d2", penwidth=2];
    }
    
    subgraph cluster_worker {
        label="Worker (Cloud Batch)";
        style=filled;
        color="#fff3e0";
        fontcolor="#e65100";
        fontsize=14;
        
        download [label="Download gs://.../run_x/raw_logs.zip", fillcolor="#ffe0b2", color="#f57c00"];
        resume [label="harbor jobs resume\n(Skips successful tasks)", fillcolor="#ffcc80", color="#ef6c00", penwidth=2];
        upload [label="Upload merged gs://.../run_x/raw_logs.zip", fillcolor="#ffe0b2", color="#f57c00"];
    }

    create_job -> download [label=" Start Worker", fontcolor="#555555", fontsize=10];
    download -> resume [color="#ff9800"];
    resume -> upload [color="#ff9800"];
}"""

# 2. BigQuery 1:MANY Schema
dot_bq = """digraph G {
    rankdir=TB;
    fontname="Helvetica,Arial,sans-serif";
    node [fontname="Helvetica,Arial,sans-serif", style="filled,rounded", shape=box, fontcolor="#333333"];
    edge [fontname="Helvetica,Arial,sans-serif", color="#666666", penwidth=1.5];

    subgraph cluster_bq {
        label="BigQuery 1:MANY Relationship";
        style=filled;
        color="#e8f5e9";
        fontcolor="#2e7d32";
        fontsize=14;
        
        jobs_table [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
            <tr><td colspan="3" bgcolor="#a5d6a7"><b>eval_results_jobs</b></td></tr>
            <tr><td><b>run_id</b></td><td><b>job_id</b></td><td><b>Status</b></td></tr>
            <tr><td>run_x</td><td>batch_1</td><td>40/80 (Failed)</td></tr>
            <tr><td>run_x</td><td bgcolor="#ffffcc">batch_2</td><td bgcolor="#ffffcc">80/80 (Success)</td></tr>
        </table>>, shape=none, margin=0];
        
        get_job [label=<<table border="0" cellborder="0" cellspacing="0">
            <tr><td align="center"><b>get_job() &amp; list_jobs()</b></td></tr>
            <tr><td align="center"><font point-size="10">SELECT * FROM (...)</font></td></tr>
            <tr><td align="center"><font point-size="10">WHERE rn = 1</font></td></tr>
            <tr><td align="center"><font point-size="10">ORDER BY updated_at DESC</font></td></tr>
        </table>>, fillcolor="#c8e6c9", color="#388e3c", penwidth=2];
    }
    
    jobs_table -> get_job [label=" UI fetches only\nthe latest attempt", fontcolor="#555555", fontsize=10];
}"""

print(f"URL_ARCH: https://quickchart.io/graphviz?graph={urllib.parse.quote(dot_arch)}")
print(f"URL_BQ: https://quickchart.io/graphviz?graph={urllib.parse.quote(dot_bq)}")
