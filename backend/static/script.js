// scripts.js
let selectedFile = null;
let cyInstance = null;

const loaderMessages = [
  "Extracting text from PDF...",
  "Generating paper summary...",
  "Extracting key concepts...",
  "Building knowledge graph...",
  "Identifying research gaps...",
  "Generating hypotheses...",
  "Designing experiments...",
  "Almost done..."
];

let loaderInterval = null;


function handleFileSelect(input) {
  selectedFile = input.files[0];
  if (selectedFile) {
    document.getElementById('file-name').textContent = `✅ ${selectedFile.name}`;
    document.getElementById('analyze-btn').disabled = false;
  }
}


async function analyzePaper() {
  if (!selectedFile) return;

  hideResults();
  hideError();
  showLoader();

  let msgIndex = 0;
  loaderInterval = setInterval(() => {
    msgIndex = (msgIndex + 1) % loaderMessages.length;
    document.getElementById('loader-text').textContent = loaderMessages[msgIndex];
  }, 2500);

  try {
    const formData = new FormData();
    formData.append('file', selectedFile);

    const response = await fetch('/analyze', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    console.log("Response:", data);

    if (!response.ok) {
      throw new Error(data.error || "Analysis failed");
    }

    displaySummary(data.summary);
    displayConcepts(data.concepts);
    displayGraph(data.graph);
    displayGaps(data.gaps);
    displayHypotheses(data.hypotheses);
    displayExperiments(data.experiments);

    document.getElementById('results').style.display = 'block';
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });

  } catch (error) {
    console.log("Error:", error.message);
    showError(error.message);
  } finally {
    hideLoader();
    clearInterval(loaderInterval);
  }
}


function displaySummary(summary) {
  document.getElementById('summary-text').textContent = summary || "No summary available";
}


function displayConcepts(concepts) {
  const container = document.getElementById('concepts-container');
  container.innerHTML = '';

  if (!concepts || concepts.length === 0) {
    container.innerHTML = '<p>No concepts found</p>';
    return;
  }

  concepts.forEach(concept => {
    const tag = document.createElement('span');
    tag.className = 'concept-tag';
    tag.textContent = concept;
    container.appendChild(tag);
  });
}


function displayGraph(graph) {
  const container = document.getElementById('cy');
  container.innerHTML = '';

  if (!graph || !graph.nodes || graph.nodes.length === 0) {
    container.innerHTML = "<p style='padding:20px;color:#888'>No graph data available</p>";
    return;
  }

  // Only keep valid edges where both nodes exist
  const nodeIds = new Set(graph.nodes);
  const validEdges = graph.edges.filter(e =>
    e.subject && e.object &&
    nodeIds.has(e.subject) &&
    nodeIds.has(e.object) &&
    e.subject !== e.object
  );

  const nodes = graph.nodes.map(n => ({
    data: {
      id: n,
      // Trim long labels to keep graph clean
      label: n.length > 18 ? n.substring(0, 18) + '...' : n
    }
  }));

  const edges = validEdges.map((e, i) => ({
    data: {
      id: `edge_${i}`,
      source: e.subject,
      target: e.object,
      label: e.relation || ''
    }
  }));

  cyInstance = cytoscape({
    container: container,
    elements: [...nodes, ...edges],

    style: [
      {
        selector: 'node',
        style: {
          'label': 'data(label)',
          'background-color': '#4A90E2',
          'color': '#fff',
          'text-valign': 'center',
          'text-halign': 'center',
          'font-size': '11px',
          'font-weight': 'bold',
          'padding': '14px',
          'text-wrap': 'wrap',
          'text-max-width': '90px',
          'width': 'label',
          'height': 'label',
          'shape': 'round-rectangle',
          'border-width': 2,
          'border-color': '#2171c7'
        }
      },
      {
        selector: 'node:hover',
        style: {
          'background-color': '#2171c7',
          'cursor': 'pointer'
        }
      },
      {
        selector: 'edge',
        style: {
          'label': 'data(label)',
          'curve-style': 'bezier',
          'target-arrow-shape': 'triangle',
          'line-color': '#94a3b8',
          'target-arrow-color': '#94a3b8',
          'font-size': '9px',
          'color': '#444',
          'text-background-color': '#fff',
          'text-background-opacity': 1,
          'text-background-padding': '3px',
          'text-border-width': 1,
          'text-border-color': '#e2e8f0',
          'text-border-opacity': 1,
          'width': 2,
          'opacity': 0.8
        }
      }
    ],

    // breadthfirst layout - best for many nodes, no overlapping
    layout: {
      name: 'breadthfirst',
      directed: true,
      padding: 50,
      spacingFactor: 1.8,  // More space between nodes
      animate: true,
      animationDuration: 800,
      fit: true
    }
  });
}


// Reset graph zoom and position
function resetGraph() {
  if (cyInstance) {
    cyInstance.reset();
  }
}

// Fit entire graph inside container
function fitGraph() {
  if (cyInstance) {
    cyInstance.fit(50);
  }
}

// Zoom in
function zoomIn() {
  if (cyInstance) {
    cyInstance.zoom(cyInstance.zoom() * 1.3);
    cyInstance.center();
  }
}

// Zoom out
function zoomOut() {
  if (cyInstance) {
    cyInstance.zoom(cyInstance.zoom() * 0.7);
    cyInstance.center();
  }
}


function displayGaps(gaps) {
  const container = document.getElementById('gaps-container');
  container.innerHTML = '';

  // Auto adjust height based on number of nodes
  const nodeCount = graph.nodes.length;
  if (nodeCount <= 5) {
    container.style.height = '300px';
  } else if (nodeCount <= 8) {
    container.style.height = '400px';
  } else {
    container.style.height = '500px';
  }

  if (!gaps || gaps.length === 0) {
    container.innerHTML = '<p>No research gaps found</p>';
    return;
  }

  gaps.forEach((gap, index) => {
    container.innerHTML += `
      <div class="gap-card">
        <div class="gap-number">${index + 1}</div>
        <p>${gap}</p>
      </div>`;
  });
}


function displayHypotheses(hypotheses) {
  const container = document.getElementById('hypotheses-container');
  container.innerHTML = '';

  if (!hypotheses || hypotheses.length === 0) {
    container.innerHTML = '<p>No hypotheses generated</p>';
    return;
  }

  hypotheses.forEach(h => {
    const levelClass = h.level ? h.level.toLowerCase() : 'basic';
    container.innerHTML += `
      <div class="hyp-card ${levelClass}">
        <div class="hyp-level">${h.level || 'Basic'} Hypothesis</div>
        <h3>${h.hypothesis || ''}</h3>
        <p><strong>Rationale:</strong> ${h.rationale || ''}</p>
      </div>`;
  });
}


function displayExperiments(experiments) {
  const container = document.getElementById('experiments-container');
  container.innerHTML = '';

  if (!experiments || experiments.length === 0) {
    container.innerHTML = '<p>No experiments generated</p>';
    return;
  }

  experiments.forEach((exp, index) => {
    const hypothesis = exp.hypothesis || '';
    container.innerHTML += `
      <div class="exp-card">
        <div class="exp-header">
          Experiment ${index + 1}: ${hypothesis.substring(0, 80)}${hypothesis.length > 80 ? '...' : ''}
        </div>
        <div class="exp-body">
          <div class="exp-field">
            <label>Objective</label>
            <p>${exp.objective || 'N/A'}</p>
          </div>
          <div class="exp-field">
            <label>Methodology</label>
            <p>${exp.methodology || 'N/A'}</p>
          </div>
          <div class="exp-field">
            <label>Required Data</label>
            <p>${exp.required_data || 'N/A'}</p>
          </div>
          <div class="exp-field">
            <label>Evaluation Metrics</label>
            <p>${exp.evaluation_metrics || 'N/A'}</p>
          </div>
          <div class="exp-field" style="grid-column: 1/-1">
            <label>Expected Outcome</label>
            <p>${exp.expected_outcome || 'N/A'}</p>
          </div>
        </div>
      </div>`;
  });
}


function showLoader() {
  document.getElementById('loader').style.display = 'block';
  document.getElementById('loader-text').textContent = loaderMessages[0];
}

function hideLoader() {
  document.getElementById('loader').style.display = 'none';
}

function hideResults() {
  document.getElementById('results').style.display = 'none';
}

function showError(message) {
  const box = document.getElementById('error-box');
  box.textContent = `❌ Error: ${message}`;
  box.style.display = 'block';
}

function hideError() {
  document.getElementById('error-box').style.display = 'none';
}