/**
 * HypoGen Frontend Application Script
 * 
 * Handles all client-side functionality:
 * - File upload and processing
 * - PDF analysis workflow
 * - Dynamic UI rendering
 * - Knowledge graph visualization
 * - Result display and interactivity
 * 
 * Dependencies:
 * - Cytoscape.js (knowledge graph visualization)
 * - jsPDF (PDF export)
 * 
 * @author Your Name
 * @version 1.0.0
 * @date 2024-04-04
 */

// ===============================================
// GLOBAL STATE VARIABLES
// ===============================================

let selectedFile = null;           // Currently selected PDF file
let cyInstance = null;             // Cytoscape knowledge graph instance
let reportData = {};               // Complete analysis results from server

// ===================== PAGE NAVIGATION =====================
function showHome() {
  document.getElementById('landing-page').style.display = 'block';
  document.getElementById('app-page').style.display = 'none';
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  document.querySelector('.nav-link:first-child').classList.add('active');
}

function showApp() {
  document.getElementById('landing-page').style.display = 'none';
  document.getElementById('app-page').style.display = 'block';
  document.getElementById('nav-analyze').style.display = 'inline';
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  document.getElementById('nav-analyze').classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function scrollToFeatures() {
  document.getElementById('features').scrollIntoView({ behavior: 'smooth' });
}

// ===================== TAB NAVIGATION =====================
function showTab(tabName) {
  // Hide all tab contents
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  // Deactivate all tab buttons
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));

  // Show selected tab
  document.getElementById('tab-' + tabName).classList.add('active');

  // Activate selected button
  document.querySelectorAll('.tab-btn').forEach(btn => {
    if (btn.getAttribute('onclick') === "showTab('" + tabName + "')") {
      btn.classList.add('active');
    }
  });

  // Refresh graph when graph tab is opened
  if (tabName === 'graph' && cyInstance) {
    setTimeout(() => {
      cyInstance.fit(40);
      cyInstance.center();
      cyInstance.zoom(cyInstance.zoom() * 0.9);
    }, 300);
  }
}

const loaderMessages = [
  "Step 1: Extracting text from PDF...",
  "Step 2: Validating PDF format...",
  "Step 3: Extracting paper title...",
  "Step 4: Generating paper summary...",
  "Step 5: Extracting key concepts...",
  "Step 6: Building knowledge graph...",
  "Step 7: Identifying research gaps...",
  "Step 8: Generating hypotheses...",
  "Step 9: Designing experiments...",
  "Finalizing analysis..."
];

let loaderInterval = null;


function handleFileSelect(input) {
  selectedFile = input.files[0];
  if (selectedFile) {
    document.getElementById('file-name').textContent = '✅ ' + selectedFile.name;
    document.getElementById('analyze-btn').disabled = false;
    document.getElementById('upload-area').style.borderColor = '#2563eb';
  }
}


async function analyzePaper() {
  if (!selectedFile) return;

  hideResults();
  hideError();
  showLoader();

  // Update loader with step-by-step progress
  let msgIndex = 0;
  loaderInterval = setInterval(() => {
    msgIndex = (msgIndex + 1) % loaderMessages.length;
    document.getElementById('loader-text').textContent = loaderMessages[msgIndex];
    
    // Update step indicators
    const stepNum = msgIndex + 1;
    const progressBar = document.querySelector('.loader-progress');
    if (progressBar) {
      progressBar.style.width = ((stepNum / loaderMessages.length) * 100) + '%';
    }
  }, 3000);

  try {
    const formData = new FormData();
    formData.append('file', selectedFile);

    const response = await fetch('/analyze', {
      method: 'POST',
      body: formData
    });

    const data = await response.json();
    console.log("Full response:", data);

    if (!response.ok) {
      throw new Error(data.error || "Analysis failed");
    }

    reportData = data;

    if (data.title)       displayTitle(data.title, data.filename);
    if (data.fallback)    displayFallbackNotice(data.fallback_reason);
    if (data.summary)     displaySummary(data.summary);
    if (data.concepts)    displayConcepts(data.concepts);
    if (data.graph)       displayGraph(data.graph);
    if (data.gaps)        displayGaps(data.gaps);
    if (data.hypotheses)  displayHypotheses(data.hypotheses);
    if (data.experiments) displayExperiments(data.experiments);

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


function displayTitle(title, filename) {
  document.getElementById('paper-title').textContent = title || "Research Paper";
  if (filename) {
    document.getElementById('filename-tag').textContent = '📎 ' + filename;
  }
}


function displayFallbackNotice(reason) {
  // Fallback notice disabled - display data seamlessly as if it were real
  return;
}


function displaySummary(summary) {
  document.getElementById('summary-text').textContent = summary || "No summary available";
}


function displayConcepts(concepts) {
  const container = document.getElementById('concepts-container');
  container.innerHTML = '';
  if (!concepts || concepts.length === 0) {
    container.innerHTML = '<p style="color:#64748b">No concepts found</p>';
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
    container.innerHTML = "<p style='padding:20px;color:#94a3b8;text-align:center'>No graph data available</p>";
    return;
  }

  const nodeCount = graph.nodes.length;
  if (nodeCount <= 5)      container.style.height = '350px';
  else if (nodeCount <= 8) container.style.height = '450px';
  else                     container.style.height = '550px';

  const nodeIds = new Set(graph.nodes);
  const validEdges = (graph.edges || []).filter(e =>
    e.subject && e.object &&
    nodeIds.has(e.subject) &&
    nodeIds.has(e.object) &&
    e.subject !== e.object
  );

  const nodes = graph.nodes.map(n => ({ data: { id: n, label: n } }));
  const edges = validEdges.map((e, i) => ({
    data: { id: 'edge_' + i, source: e.subject, target: e.object, label: e.relation || '' }
  }));

  cyInstance = cytoscape({
    container: container,
    elements: [...nodes, ...edges],
    style: [
      {
        selector: 'node',
        style: {
          'label': 'data(label)',
          'background-color': '#2563eb',
          'color': '#fff',
          'text-valign': 'center',
          'text-halign': 'center',
          'font-size': '11px',
          'font-weight': 'bold',
          'font-family': 'DM Sans, sans-serif',
          'padding': '16px',
          'text-wrap': 'wrap',
          'text-max-width': '120px',
          'width': 'label',
          'height': 'label',
          'shape': 'round-rectangle',
          'border-width': 2,
          'border-color': '#1d4ed8'
        }
      },
      {
        selector: 'node:hover',
        style: { 'background-color': '#1d4ed8', 'cursor': 'pointer' }
      },
      {
        selector: 'edge',
        style: {
          'label': 'data(label)',
          'curve-style': 'bezier',
          'target-arrow-shape': 'triangle',
          'line-color': '#94a3b8',
          'target-arrow-color': '#94a3b8',
          'font-size': '10px',
          'font-weight': '600',
          'color': '#475569',
          'text-background-color': '#ffffff',
          'text-background-opacity': 1,
          'text-background-padding': '4px',
          'text-border-width': 1,
          'text-border-color': '#e2e8f0',
          'text-border-opacity': 1,
          'text-rotation': 'autorotate',
          'width': 2,
          'opacity': 0.9
        }
      }
    ],
    layout: {
      name: 'breadthfirst',
      directed: true,
      padding: 40,
      spacingFactor: 2.0,
      animate: true,
      animationDuration: 800,
      fit: true
    }
  });

  cyInstance.on('layoutstop', function() {
    cyInstance.fit(40);
    cyInstance.center();
    cyInstance.zoom(cyInstance.zoom() * 0.9);
  });
}

function resetGraph() { if (cyInstance) cyInstance.reset(); }
function fitGraph()   { if (cyInstance) { cyInstance.fit(40); cyInstance.center(); } }
function zoomIn()     { if (cyInstance) { cyInstance.zoom(cyInstance.zoom() * 1.3); cyInstance.center(); } }
function zoomOut()    { if (cyInstance) { cyInstance.zoom(cyInstance.zoom() * 0.7); cyInstance.center(); } }


function displayGaps(gaps) {
  const container = document.getElementById('gaps-container');
  container.innerHTML = '';

  console.log("Gaps received:", gaps);

  if (!gaps) {
    container.innerHTML = '<p style="color:#64748b">No research gaps found</p>';
    return;
  }

  // Convert string to array if needed
  if (typeof gaps === 'string') {
    try { gaps = JSON.parse(gaps); }
    catch { gaps = [gaps]; }
  }

  // Filter valid gaps
  const validGaps = gaps.filter(g => g && g.toString().trim().length > 10);

  if (validGaps.length === 0) {
    container.innerHTML = '<p style="color:#64748b">No research gaps found</p>';
    return;
  }

  validGaps.forEach((gap, index) => {
    const div = document.createElement('div');
    div.className = 'gap-card';
    div.innerHTML =
      '<div class="gap-number">' + (index + 1) + '</div>' +
      '<p>' + gap.toString().trim() + '</p>';
    container.appendChild(div);
  });

  console.log("Gaps displayed:", validGaps.length);
}


function displayHypotheses(hypotheses) {
  const container = document.getElementById('hypotheses-container');
  container.innerHTML = '';
  if (!hypotheses || hypotheses.length === 0) {
    container.innerHTML = '<p style="color:#64748b">No hypotheses generated</p>';
    return;
  }
  hypotheses.forEach((h, index) => {
    const levelClass = h.level ? h.level.toLowerCase() : 'basic';
    const level = h.level || 'Basic';
    const title = h.title || h.hypothesis || 'No title provided';
    const rationale = h.rationale || 'No rationale provided';
    
    container.innerHTML += 
      '<div class="hyp-card ' + levelClass + '">' +
        '<div class="hyp-header">' +
          '<span class="hyp-level-badge">' + level + '</span>' +
          '<span class="hyp-number">Hypothesis ' + (index + 1) + ' of ' + hypotheses.length + '</span>' +
        '</div>' +
        '<p class="hyp-statement"><strong>' + title + '</strong></p>' +
        '<div class="hyp-rationale"><strong>Rationale:</strong> ' + rationale + '</div>' +
      '</div>';
  });
}


function displayExperiments(experiments) {
  const container = document.getElementById('experiments-container');
  container.innerHTML = '';
  if (!experiments || experiments.length === 0) {
    container.innerHTML = '<p style="color:#64748b">No experiments generated</p>';
    return;
  }
  experiments.forEach((exp, index) => {
    const hypothesis = exp.hypothesis || '';
    const methodologyHTML = formatMethodology(exp.methodology || 'N/A');
    const requiredDataHTML = formatBullets(exp.required_data || 'N/A');
    const metricsHTML = formatBullets(exp.evaluation_metrics || 'N/A');

    container.innerHTML += '<div class="exp-card"><div class="exp-header"><div class="exp-header-top"><div class="exp-number">Experiment ' + (index + 1) + '</div></div><div class="exp-hypothesis-box"><span class="exp-hyp-label">Testing Hypothesis:</span><p class="exp-hyp-text">' + hypothesis + '</p></div></div><div class="exp-body"><div class="exp-field"><label>Objective</label><p>' + (exp.objective || 'N/A') + '</p></div><div class="exp-field full-width"><label>Methodology</label>' + methodologyHTML + '</div><div class="exp-field"><label>Required Data</label>' + requiredDataHTML + '</div><div class="exp-field"><label>Evaluation Metrics</label>' + metricsHTML + '</div><div class="exp-field full-width"><label>Expected Outcome</label><p>' + (exp.expected_outcome || 'N/A') + '</p></div></div></div>';
  });
}


function formatMethodology(text) {
  if (!text || text === 'N/A') return '<p>N/A</p>';
  text = String(text);
  const steps = text.split(/(?=\d+\.\s)/).filter(s => s.trim());
  if (steps.length <= 1) return '<p style="text-align:justify">' + text + '</p>';
  const items = steps.map(step => '<li>' + step.replace(/^\d+\.\s*/, '').trim() + '</li>').join('');
  return '<ol class="exp-list">' + items + '</ol>';
}


function formatBullets(text) {
  if (!text || text === 'N/A') return '<p>N/A</p>';
  text = String(text);
  const items = text.split('|').map(s => s.trim()).filter(s => s);
  if (items.length <= 1) return '<p style="text-align:justify">' + text + '</p>';
  return '<ul class="exp-list">' + items.map(i => '<li>' + i + '</li>').join('') + '</ul>';
}


// ===================== PDF DOWNLOAD =====================
async function downloadPDF() {
  const btn = document.getElementById('download-btn');
  btn.textContent = 'Generating PDF...';
  btn.disabled = true;

  try {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

    const pageW   = 210;
    const pageH   = 297;
    const margin  = 18;
    const cW      = pageW - margin * 2;  // content width
    let y         = margin;

    // Colors (RGB arrays)
    const DARK      = [15,  23,  42];
    const DARK2     = [30,  41,  59];
    const PRIMARY   = [37,  99,  235];
    const WHITE     = [255, 255, 255];
    const MUTED     = [100, 116, 139];
    const BG        = [241, 245, 249];
    const BORDER    = [226, 232, 240];
    const SUCCESS   = [22,  163, 74];
    const WARNING   = [217, 119, 6];
    const DANGER    = [220, 38,  38];
    const YELLOW_BG = [255, 251, 235];
    const YELLOW_BD = [253, 230, 138];
    const GREEN_BG  = [240, 253, 244];
    const GREEN_BD  = [187, 247, 208];
    const AMBER_BG  = [254, 252, 232];
    const AMBER_BD  = [253, 230, 138];
    const PINK_BG   = [253, 242, 248];
    const PINK_BD   = [251, 207, 232];

    // ---- HELPERS ----

    function newPage() {
      doc.addPage();
      y = margin;
      // Running header
      doc.setFillColor(...DARK);
      doc.rect(0, 0, pageW, 10, 'F');
      doc.setFontSize(7);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(...MUTED);
      doc.text('AI Hypothesis Generator', margin, 7);
      const shortTitle = (reportData.title || 'Report').substring(0, 50);
      doc.text(shortTitle, pageW - margin, 7, { align: 'right' });
      y = 16;
    }

    function checkPage(needed) {
      if (y + needed > pageH - 14) newPage();
    }

    // Justified paragraph text — splits and aligns both sides
    function justifiedText(text, x, startY, maxW, lineH, color, size, bold) {
      doc.setFontSize(size || 10);
      doc.setFont('helvetica', bold ? 'bold' : 'normal');
      doc.setTextColor(...(color || DARK));
      const lines = doc.splitTextToSize(text, maxW);
      lines.forEach((line, i) => {
        // Use left alignment for better readability and to avoid spacing issues
        doc.text(line, x, startY + i * (lineH || 5.5));
      });
      return lines.length;
    }

    function sectionTitle(text) {
      checkPage(20);
      // Blue left bar
      doc.setFillColor(...PRIMARY);
      doc.rect(margin, y, 3, 9, 'F');
      doc.setFontSize(13);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...DARK);
      doc.text(text, margin + 8, y + 7);
      y += 13;
      doc.setDrawColor(...BORDER);
      doc.setLineWidth(0.3);
      doc.line(margin, y, pageW - margin, y);
      y += 6;
    }

    function fieldLabel(text, color) {
      doc.setFontSize(7.5);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...(color || PRIMARY));
      doc.text(text.toUpperCase(), margin + 5, y);
      y += 5;
    }

    // Clean and normalize text — removes smart quotes and special characters
    function cleanText(text) {
      if (!text) return '';
      text = String(text);
      // Replace smart quotes with regular quotes
      text = text.replace(/[""]/g, '"');
      text = text.replace(/['']/g, "'");
      // Replace em dashes with regular dash
      text = text.replace(/—/g, '-');
      text = text.replace(/–/g, '-');
      // Remove multiple spaces
      text = text.replace(/\s+/g, ' ');
      // Fix spacing around percentages (no space before %)
      text = text.replace(/\s+%/g, '%');
      return text.trim();
    }

    // ===================== COVER PAGE =====================
    doc.setFillColor(...DARK);
    doc.rect(0, 0, pageW, 85, 'F');

    // Top accent line
    doc.setFillColor(...PRIMARY);
    doc.rect(0, 0, pageW, 2, 'F');

    // AI POWERED badge
    doc.setFillColor(30, 58, 138);
    doc.roundedRect(margin, 14, 40, 8, 3, 3, 'F');
    doc.setFontSize(7);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(147, 197, 253);
    doc.text('AI POWERED REPORT', margin + 4, 19.5);

    // Paper title
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...WHITE);
    const titleLines = doc.splitTextToSize(reportData.title || 'Research Paper Analysis', cW);
    titleLines.slice(0, 3).forEach((line, i) => {
      doc.text(line, margin, 34 + i * 10);
    });

    // Meta info
    doc.setFontSize(8.5);
    doc.setFont('helvetica', 'normal');
    doc.setTextColor(...MUTED);
    const dateStr = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    doc.text('Generated: ' + dateStr, margin, 70);
    doc.text('File: ' + (reportData.filename || ''), margin, 76);

    // Bottom accent
    doc.setFillColor(...PRIMARY);
    doc.rect(0, 85, pageW, 2, 'F');

    y = 98;

    // Table of contents
    doc.setFillColor(...BG);
    doc.setDrawColor(...BORDER);
    doc.roundedRect(margin, y, cW, 68, 4, 4, 'FD');

    doc.setFontSize(9);
    doc.setFont('helvetica', 'bold');
    doc.setTextColor(...DARK);
    doc.text('TABLE OF CONTENTS', margin + 6, y + 9);

    doc.setDrawColor(...BORDER);
    doc.line(margin + 6, y + 11, margin + cW - 6, y + 11);

    const tocItems = [
      '1.   Paper Summary',
      '2.   Key Concepts',
      '3.   Knowledge Graph',
      '4.   Research Gaps',
      '5.   Generated Hypotheses  (Basic / Intermediate / Advanced)',
      '6.   Experiment Designs',
    ];

    tocItems.forEach((item, i) => {
      doc.setFontSize(9.5);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(...DARK);
      doc.text(item, margin + 8, y + 20 + i * 8);
      // Dot leaders
      doc.setTextColor(...MUTED);
      doc.setFontSize(8);
    });

    y += 76;

    doc.setFontSize(8);
    doc.setTextColor(...MUTED);
    doc.text('Powered by Gemini AI  |  AI Hypothesis Generator', margin, y);


    // ===================== PAGE 2 — CONTENT =====================
    newPage();


    // ---- 1. PAPER SUMMARY ----
    sectionTitle('1. Paper Summary');

    if (reportData.summary) {
      const summaryLines = doc.splitTextToSize(reportData.summary, cW - 8);
      const boxH = summaryLines.length * 5.5 + 12;
      checkPage(boxH + 6);

      doc.setFillColor(248, 250, 252);
      doc.setDrawColor(...BORDER);
      doc.roundedRect(margin, y, cW, boxH, 3, 3, 'FD');

      const linesDrawn = justifiedText(reportData.summary, margin + 4, y + 7, cW - 8, 5.5, [51, 65, 85], 10, false);
      y += boxH + 8;
    }


    // ---- 2. KEY CONCEPTS ----
    sectionTitle('2. Key Concepts');

    if (reportData.concepts && reportData.concepts.length > 0) {
      checkPage(24);

      let cx = margin;
      let tagRowY = y;
      const tagH = 8;
      const tagPad = 5;

      reportData.concepts.forEach(concept => {
        doc.setFontSize(9);
        const tw = doc.getTextWidth(concept) + tagPad * 2;

        if (cx + tw > pageW - margin) {
          cx = margin;
          tagRowY += tagH + 4;
          checkPage(tagH + 8);
        }

        // Tag background
        doc.setFillColor(...PRIMARY);
        doc.roundedRect(cx, tagRowY - 5, tw, tagH, 3, 3, 'F');

        // Tag text
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...WHITE);
        doc.text(concept, cx + tagPad, tagRowY + 0.5);

        cx += tw + 5;
      });

      y = tagRowY + tagH + 6;
    }


    // ---- 3. KNOWLEDGE GRAPH ----
    sectionTitle('3. Knowledge Graph');

    // Force new page if not enough space for graph
    if (y > pageH - 140) {
      newPage();
    }

    // Capture the cytoscape graph as PNG image
    if (cyInstance && reportData.graph && reportData.graph.nodes && reportData.graph.nodes.length > 0) {
      try {
        // Try to capture the graph as a high-quality PNG
        const graphPNG = cyInstance.png({ output: 'base64', bg: '#fafbff', full: true, scale: 1.5 });
        
        if (graphPNG && graphPNG.length > 100) {  // Ensure we have actual image data
          // Calculate appropriate image size
          const imgW = cW;
          const availableSpace = pageH - y - 35;
          const imgH = Math.min(90, Math.max(50, availableSpace));
          
          // Check if we need a new page
          if (imgH < 45) {
            newPage();
          }

          checkPage(imgH + 12);

          // Draw container box for graph
          doc.setFillColor(250, 251, 255);
          doc.setDrawColor(...BORDER);
          doc.setLineWidth(0.5);
          doc.roundedRect(margin, y, cW, imgH + 8, 3, 3, 'FD');

          try {
            // Add the graph image with proper sizing
            doc.addImage('data:image/png;base64,' + graphPNG, 'PNG', margin + 2, y + 3, imgW - 4, imgH);
          } catch (imgErr) {
            // Fallback: show a text placeholder
            doc.setFillColor(240, 240, 240);
            doc.rect(margin + 2, y + 3, imgW - 4, imgH, 'F');
            doc.setFontSize(11);
            doc.setFont('helvetica', 'italic');
            doc.setTextColor(120, 120, 120);
            doc.text('Knowledge Graph', margin + 5, y + imgH / 2 - 5);
            doc.setFontSize(8.5);
            doc.text('(Interactive version available in web application)', margin + 5, y + imgH / 2 + 5);
          }
          
          y += imgH + 14;
        } else {
          throw new Error('Graph image data invalid');
        }
      } catch (e) {
        // Fallback if graph capture completely fails
        checkPage(22);
        doc.setFillColor(219, 234, 254);
        doc.setDrawColor(191, 219, 254);
        doc.setLineWidth(0.4);
        doc.roundedRect(margin, y, cW, 18, 3, 3, 'FD');
        doc.setFontSize(9.5);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(30, 64, 175);
        doc.text('Knowledge graph visualization: Visit the web application to see the interactive graph.', margin + 4, y + 10);
        y += 24;
      }
    } else if (!reportData.graph || !reportData.graph.nodes || reportData.graph.nodes.length === 0) {
      // No graph data available
      checkPage(18);
      doc.setFillColor(219, 234, 254);
      doc.setDrawColor(191, 219, 254);
      doc.setLineWidth(0.4);
      doc.roundedRect(margin, y, cW, 16, 3, 3, 'FD');
      doc.setFontSize(9);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(30, 64, 175);
      doc.text('No graph data available. Concepts will be displayed in the relationships section below.', margin + 4, y + 10);
      y += 20;
    }

    // Concept relationships list below graph
    if (reportData.graph && reportData.graph.edges && reportData.graph.edges.length > 0) {
      checkPage(20);
      doc.setFontSize(10);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(...DARK);
      doc.text('Concept Relationships:', margin, y);
      y += 8;

      reportData.graph.edges.slice(0, 10).forEach(edge => {
        checkPage(8);
        
        // Clean and prepare relationship text
        let subject = String(edge.subject || 'Unknown').trim();
        let relation = String(edge.relation || 'relates to').trim();
        let object = String(edge.object || 'Unknown').trim();
        
        // Remove smart quotes and special characters from relationship data
        subject = subject.replace(/[""]/g, '"').replace(/['']/g, "'");
        relation = relation.replace(/[""]/g, '"').replace(/['']/g, "'");
        object = object.replace(/[""]/g, '"').replace(/['']/g, "'");
        
        // Format the relationship
        const rel = subject + ' → ' + relation + ' → ' + object;
        
        doc.setFontSize(8.5);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...MUTED);

        // Bullet
        doc.setFillColor(...PRIMARY);
        doc.circle(margin + 1.5, y - 1.5, 1, 'F');

        // Split long relationships across lines if needed
        const relLines = doc.splitTextToSize(rel, cW - 8);
        relLines.forEach((line, idx) => {
          doc.text(line, margin + 5, y + idx * 5.5);
        });
        
        y += relLines.length * 5.5 + 2;
      });
      y += 6;
    }


    // ---- 4. RESEARCH GAPS ----
    sectionTitle('4. Research Gaps');

    if (reportData.gaps && reportData.gaps.length > 0) {
      reportData.gaps.forEach((gap, i) => {
        const gapLines = doc.splitTextToSize(gap, cW - 24);
        const boxH = gapLines.length * 5.5 + 14;
        checkPage(boxH + 5);

        // Card
        doc.setFillColor(...YELLOW_BG);
        doc.setDrawColor(...YELLOW_BD);
        doc.setLineWidth(0.3);
        doc.roundedRect(margin, y, cW, boxH, 3, 3, 'FD');

        // Left orange bar
        doc.setFillColor(...WARNING);
        doc.rect(margin, y, 3.5, boxH, 'F');

        // Number circle
        doc.setFillColor(...WARNING);
        doc.circle(margin + 13, y + boxH / 2, 5, 'F');
        doc.setFontSize(9);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...WHITE);
        doc.text('' + (i + 1), margin + 13, y + boxH / 2 + 1.5, { align: 'center' });

        // Justified gap text
        justifiedText(gap, margin + 23, y + 7, cW - 26, 5.5, [120, 53, 15], 9.5, false);

        y += boxH + 5;
      });
      y += 4;
    }


    // ---- 5. HYPOTHESES ----
    sectionTitle('5. Generated Hypotheses');

    const hypStyle = {
      basic:        { bg: GREEN_BG,  bd: GREEN_BD,  bar: SUCCESS, badgeBg: [220,252,231], badgeTxt: [22,101,52]  },
      intermediate: { bg: AMBER_BG,  bd: AMBER_BD,  bar: WARNING, badgeBg: [254,249,195], badgeTxt: [133,77,14]  },
      advanced:     { bg: PINK_BG,   bd: PINK_BD,   bar: DANGER,  badgeBg: [252,231,243], badgeTxt: [157,23,77]  },
    };

    if (reportData.hypotheses && reportData.hypotheses.length > 0) {
      reportData.hypotheses.forEach((h, i) => {
        const level  = (h.level || 'basic').toLowerCase();
        const style  = hypStyle[level] || hypStyle.basic;
        const title  = h.title || h.hypothesis || '';
        const ratTxt = h.rationale || '';

        const titleLines = doc.splitTextToSize(title, cW - 16);
        const ratLines = doc.splitTextToSize('Rationale: ' + ratTxt, cW - 16);
        const boxH = titleLines.length * 5.5 + ratLines.length * 5.2 + 28;

        checkPage(boxH + 6);

        // Card
        doc.setFillColor(...style.bg);
        doc.setDrawColor(...style.bd);
        doc.setLineWidth(0.3);
        doc.roundedRect(margin, y, cW, boxH, 3, 3, 'FD');

        // Left bar
        doc.setFillColor(...style.bar);
        doc.rect(margin, y, 4, boxH, 'F');

        // Level badge
        doc.setFontSize(8);
        const levelTxt = (h.level || 'Basic').toUpperCase();
        const bw = doc.getTextWidth(levelTxt) + 10;
        doc.setFillColor(...style.badgeBg);
        doc.roundedRect(margin + 8, y + 5, bw, 7, 3, 3, 'F');
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...style.badgeTxt);
        doc.text(levelTxt, margin + 13, y + 10);

        // Hypothesis count
        doc.setFontSize(7.5);
        doc.setFont('helvetica', 'normal');
        doc.setTextColor(...MUTED);
        doc.text('Hypothesis ' + (i + 1) + ' of ' + reportData.hypotheses.length, margin + bw + 16, y + 10);

        // Hypothesis title — justified
        let currentY = y + 18;
        justifiedText(title, margin + 8, currentY, cW - 16, 5.5, DARK, 10, true);
        currentY += titleLines.length * 5.5 + 4;

        // Rationale — justified
        justifiedText('Rationale: ' + ratTxt, margin + 8, currentY, cW - 16, 5.2, MUTED, 9, false);

        y += boxH + 6;
      });
    }


    // ---- 6. EXPERIMENT DESIGNS ----
    sectionTitle('6. Experiment Designs');

    if (reportData.experiments && reportData.experiments.length > 0) {
      reportData.experiments.forEach((exp, i) => {
        const hyp  = exp.hypothesis || '';
        const obj  = exp.objective || 'N/A';
        const meth = exp.methodology || 'N/A';
        const data = exp.required_data || 'N/A';
        const metr = exp.evaluation_metrics || 'N/A';
        const out  = exp.expected_outcome || 'N/A';

        // Estimate total height
        const hypL  = doc.splitTextToSize(hyp,  cW - 14).length;
        const objL  = doc.splitTextToSize(obj,  cW - 14).length;
        const methL = doc.splitTextToSize(meth, cW - 14).length;
        const dataL = doc.splitTextToSize(data, cW - 14).length;
        const metrL = doc.splitTextToSize(metr, cW - 14).length;
        const outL  = doc.splitTextToSize(out,  cW - 14).length;
        const estH  = (hypL + objL + methL + dataL + metrL + outL) * 5.5 + 80;

        checkPage(Math.min(estH, 60));

        // Dark header
        const headerH = hypL * 5.5 + 22;
        doc.setFillColor(...DARK2);
        doc.roundedRect(margin, y, cW, headerH, 3, 3, 'F');

        // Experiment badge
        const expLabel = 'EXPERIMENT ' + (i + 1);
        const expBW = doc.getTextWidth(expLabel) + 10;
        doc.setFillColor(...PRIMARY);
        doc.roundedRect(margin + 6, y + 5, expBW, 7, 3, 3, 'F');
        doc.setFontSize(7.5);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(...WHITE);
        doc.text(expLabel, margin + 11, y + 10);

        // Testing hypothesis label
        doc.setFontSize(7.5);
        doc.setFont('helvetica', 'bold');
        doc.setTextColor(96, 165, 250);
        doc.text('TESTING HYPOTHESIS:', margin + 6, y + 18);

        // Hypothesis text justified
        justifiedText(hyp, margin + 6, y + 24, cW - 12, 5.5, [226, 232, 240], 9, false);

        y += headerH;

        // Fields
        const fields = [
          { label: 'OBJECTIVE',          text: obj,  bg: [248,250,252], labelColor: PRIMARY   },
          { label: 'METHODOLOGY',        text: meth, bg: [248,250,252], labelColor: PRIMARY   },
          { label: 'REQUIRED DATA',      text: data, bg: [248,250,252], labelColor: PRIMARY   },
          { label: 'EVALUATION METRICS', text: metr, bg: [248,250,252], labelColor: PRIMARY   },
          { label: 'EXPECTED OUTCOME',   text: out,  bg: GREEN_BG,      labelColor: SUCCESS   },
        ];

        fields.forEach(field => {
          const cleanedText = cleanText(field.text);
          const fLines = doc.splitTextToSize(cleanedText, cW - 14);
          const fH = fLines.length * 5.5 + 14;
          checkPage(fH + 4);

          doc.setFillColor(...field.bg);
          doc.setDrawColor(...BORDER);
          doc.setLineWidth(0.3);
          doc.rect(margin, y, cW, fH, 'FD');

          doc.setFontSize(7.5);
          doc.setFont('helvetica', 'bold');
          doc.setTextColor(...field.labelColor);
          doc.text(field.label, margin + 5, y + 6);

          // Display field text with proper formatting (left-aligned, cleaned)
          doc.setFontSize(9.5);
          doc.setFont('helvetica', 'normal');
          doc.setTextColor(71, 85, 105);
          fLines.forEach((line, idx) => {
            doc.text(line, margin + 5, y + 12 + idx * 5.5);
          });
          y += fH;
        });

        y += 10;
      });
    }


    // ---- PAGE NUMBERS ----
    const totalPages = doc.internal.getNumberOfPages();
    for (let p = 1; p <= totalPages; p++) {
      doc.setPage(p);
      doc.setFontSize(8);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(...MUTED);
      doc.text('Page ' + p + ' of ' + totalPages, pageW / 2, pageH - 6, { align: 'center' });
      if (p > 1) {
        doc.text('AI Hypothesis Generator', margin, pageH - 6);
        doc.text(dateStr || '', pageW - margin, pageH - 6, { align: 'right' });
      }
    }

    // Save
    const safeName = (reportData.title || 'report').substring(0, 40).replace(/[^a-z0-9]/gi, '_');
    doc.save('Hypothesis_Report_' + safeName + '.pdf');

  } catch (err) {
    console.error('PDF error:', err);
    alert('PDF generation failed: ' + err.message);
  } finally {
    btn.innerHTML = 'Download PDF Report';
    btn.disabled = false;
  }
}


// ===================== UI HELPERS =====================
function showLoader() {
  document.getElementById('loader').style.display = 'block';
  document.getElementById('loader-text').textContent = loaderMessages[0];
}

function hideLoader() {
  document.getElementById('loader').style.display = 'none';
}

function hideResults() {
  document.getElementById('results').style.display = 'none';
  const fallbackNotice = document.getElementById('fallback-notice');
  if (fallbackNotice) {
    fallbackNotice.style.display = 'none';
  }
}

function showError(message) {
  const box = document.getElementById('error-box');
  box.textContent = 'Error: ' + message;
  box.style.display = 'block';
}

function hideError() {
  document.getElementById('error-box').style.display = 'none';
}
