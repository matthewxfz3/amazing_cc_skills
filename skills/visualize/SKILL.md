---
name: visualize
description: Generate shareable visualizations — diagrams via Kroki.io (instant URL) or interactive charts via Chart.js uploaded to GCS. Use when the user mentions 'diagram,' 'chart,' 'visualize,' 'graph,' 'flowchart,' 'infographic,' 'dashboard,' 'mermaid,' 'architecture diagram,' 'show me a chart,' 'create a diagram,' 'visualize this data,' or 'shareable link.' Also use when the user wants to visualize rankings, data, processes, or relationships.
---

# Visualize

Generate shareable visualizations with zero friction. Two rendering paths based on what the user needs.

## Step 1: Determine the visualization type

Ask yourself (or the user if unclear):

| If they want... | Use | Output |
|-----------------|-----|--------|
| Flowchart, architecture, sequence, ER diagram, state diagram, mind map, Gantt, class diagram | **Kroki.io** (Mermaid) | Shareable SVG/PNG URL |
| Bar chart, line chart, pie chart, doughnut, scatter, radar, interactive dashboard | **Chart.js on GCS** | Shareable HTML URL |
| Both (diagram + data charts) | **Both** | Two links |

## Path A: Kroki.io Diagram (instant, free, no auth)

### How it works
The diagram source code is compressed and encoded into the URL itself. No storage, no account, no upload.

### Generate the link

```python
import base64, zlib

diagram = '''graph TD
    A[Start] --> B[Process]
    B --> C{Decision}
    C -->|Yes| D[Result A]
    C -->|No| E[Result B]
'''

compressed = zlib.compress(diagram.encode('utf-8'), 9)
encoded = base64.urlsafe_b64encode(compressed).decode('ascii')

svg_url = f"https://kroki.io/mermaid/svg/{encoded}"
png_url = f"https://kroki.io/mermaid/png/{encoded}"
```

### Supported diagram types via Kroki
- `mermaid` — flowcharts, sequence, Gantt, ER, state, class, pie, mindmap, timeline
- `plantuml` — UML diagrams
- `graphviz/dot` — graph layouts
- `d2` — declarative diagrams
- `excalidraw` — hand-drawn style

Change the URL path: `https://kroki.io/{format}/svg/{encoded}`

### Limitations
- URL max ~4096 chars (use POST for larger diagrams)
- Static image only (no interactivity)
- No authentication needed
- Free, no rate limits published

### Always provide both links to the user:
- SVG link (scalable, sharp)
- PNG link (universal compatibility)

## Path B: Chart.js on GCS (interactive, hosted)

### How it works
Generate an HTML file with Chart.js, upload to GCS bucket, return public URL.

### Prerequisites
- GCS MCP tools connected (`mcp__gcs__upload_object_safe` or `mcp__gcs__write_object_safe`)
- A public-readable GCS bucket (default: `shareable-ai-marketing-viz`)

### Generate the chart

1. Build an HTML file with Chart.js CDN:
```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { font-family: sans-serif; background: #0f172a; color: #e2e8f0; padding: 24px; }
    .card { background: #1e293b; border-radius: 12px; padding: 24px; max-width: 800px; margin: 0 auto; }
  </style>
</head>
<body>
  <div class="card">
    <canvas id="chart"></canvas>
  </div>
  <script>
    new Chart(document.getElementById('chart'), {
      type: 'bar',  // bar, line, pie, doughnut, radar, scatter, bubble
      data: {
        labels: ['A', 'B', 'C'],
        datasets: [{ label: 'Values', data: [10, 20, 30], backgroundColor: ['#ef4444','#3b82f6','#22c55e'] }]
      },
      options: { responsive: true }
    });
  </script>
</body>
</html>
```

2. Write the HTML to a temp file:
```bash
# Write to /tmp/chart.html
```

3. Upload to GCS:
```
Use mcp__gcs__upload_object_safe:
  bucket_name: shareable-ai-marketing-viz
  file_path: /tmp/chart.html
  object_name: charts/{descriptive-name}.html
  content_type: text/html
```

4. Return the shareable URL:
```
https://storage.googleapis.com/shareable-ai-marketing-viz/charts/{descriptive-name}.html
```

### GCS bucket config
- Bucket: `shareable-ai-marketing-viz`
- Project: `ai-for-marketing-468406`
- Public access: allUsers have `roles/storage.objectViewer`
- Cost: effectively $0 (first 1GB egress free)

### If the bucket doesn't exist or isn't public
```bash
gcloud storage buckets create gs://shareable-ai-marketing-viz --project=ai-for-marketing-468406
gcloud storage buckets add-iam-policy-binding gs://shareable-ai-marketing-viz --member=allUsers --role=roles/storage.objectViewer
```

### Note on object names
`mcp__gcs__write_object_safe` and `mcp__gcs__upload_object_safe` FAIL if the object already exists. Use unique names:
- `charts/rankings-2026-03-22.html`
- `charts/phase-distribution-v2.html`
- Include a timestamp or version to avoid collisions

## Chart Design Guidelines

### Dark theme (default)
```css
background: #0f172a;
card background: #1e293b;
text: #e2e8f0;
grid lines: #334155;
accent: #38bdf8;
```

### Color palette for data
```javascript
['#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899']
```

### Responsive
Always include `<meta name="viewport" content="width=device-width, initial-scale=1.0">` and use `responsive: true` in Chart.js options.

## Output Format

Always provide the user with:

1. **The shareable link** (clickable)
2. **What it shows** (1-sentence description)
3. **How to update** (re-run the command / re-upload)

Example response:
```
Here's your visualization:

**Dashboard**: https://storage.googleapis.com/shareable-ai-marketing-viz/charts/rankings.html
Shows the top 20 skills ranked by score with tier color coding.

**Architecture**: https://kroki.io/mermaid/svg/eNp...
Shows the data flow from rank.sh through rankings.json to generated docs.

To update, re-run the visualization with new data.
```
