import urllib.parse

dot_arch = """digraph G {
    rankdir=LR;
    fontname="Helvetica,Arial,sans-serif";
    node [fontname="Helvetica,Arial,sans-serif", style="filled,rounded", shape=box, fontcolor="#333333"];
    edge [fontname="Helvetica,Arial,sans-serif", color="#666666", penwidth=1.5];

    subgraph cluster_gcs {
        label="GCS Bucket (Object Versioning ENABLED)";
        style=filled;
        color="#e8f5e9";
        fontcolor="#2e7d32";
        fontsize=14;
        
        gcs_old [label=<<table border="0" cellborder="0" cellspacing="0">
            <tr><td align="center"><b>gs://bucket/run_123/raw_logs.zip</b></td></tr>
            <tr><td align="center"><font point-size="10" color="red">(Archived v1 - Failed State)</font></td></tr>
        </table>>, fillcolor="#ffcdd2", color="#c62828"];
        
        gcs_new [label=<<table border="0" cellborder="0" cellspacing="0">
            <tr><td align="center"><b>gs://bucket/run_123/raw_logs.zip</b></td></tr>
            <tr><td align="center"><font point-size="10" color="green">(Latest v2 - Healed State)</font></td></tr>
        </table>>, fillcolor="#c8e6c9", color="#2e7d32"];
    }

    subgraph cluster_worker {
        label="Heal Worker (Cloud Batch)";
        style=filled;
        color="#fff3e0";
        fontcolor="#e65100";
        fontsize=14;
        
        download [label="1. Download Latest", fillcolor="#ffe0b2", color="#f57c00"];
        resume [label="2. harbor jobs resume\n(Merges new successes)", fillcolor="#ffcc80", color="#ef6c00", penwidth=2];
        upload [label="3. Overwrite File", fillcolor="#ffe0b2", color="#f57c00"];
    }

    gcs_old -> download [label=" Pulls v1", fontcolor="#555555", fontsize=10];
    download -> resume;
    resume -> upload;
    upload -> gcs_new [label=" Pushes v2", fontcolor="#555555", fontsize=10];
    gcs_old -> gcs_new [style=dotted, label=" GCS Auto-Archives", fontcolor="#555555", fontsize=10];
}"""

print(f"URL_ARCH: https://quickchart.io/graphviz?graph={urllib.parse.quote(dot_arch)}")
