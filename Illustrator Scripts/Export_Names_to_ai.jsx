// Illustrator JSX Script: Batch Export SVG with Name Replacement
#target illustrator

// === CONFIGURATION ===
var csvFilePath = "C:\1.Automations\Illustrator Scripts\1_ProcessedOrders.csv"; // <-- Update this to the real path

var doc = app.activeDocument;

// Read CSV
function readCSV(filePath) {
    var file = new File(filePath);
    if (!file.exists) {
        alert("CSV file not found at: " + filePath);
        return [];
    }

    file.open('r');
    var lines = [];
    while (!file.eof) {
        lines.push(file.readln());
    }
    file.close();
    return lines;
}

// Get layer by exact name
function getTextFrameFromLayer(doc, layerName) {
    var targetLayer = doc.layers.getByName(layerName);
    for (var i = 0; i < targetLayer.textFrames.length; i++) {
        return targetLayer.textFrames[i];
    }
    return null;
}

// Save as SVG
function exportToSVG(savePath) {
    var options = new ExportOptionsSVG();
    options.embedRasterImages = true;
    var destFile = new File(savePath);
    app.activeDocument.exportFile(destFile, ExportType.SVG, options);
}

// Main
var rows = readCSV(csvFilePath);
if (rows.length < 2) {
    alert("CSV must have at least one data row.");
} else {
    var header = rows[0].split(",");
    var filenameIndex = header.indexOf("Filename");

    if (filenameIndex === -1) {
        alert("Filename column not found.");
    } else {
        for (var i = 1; i < rows.length; i++) {
            var cols = rows[i].split(",");
            if (cols.length <= filenameIndex) continue;

            var fullValue = cols[filenameIndex].replace(/"/g, ''); // Remove quotes
            var firstWord = fullValue.split(" ")[0]; // Get first word

            // Set text in the layer
            var textFrame = getTextFrameFromLayer(doc, "Name<Radial Repeat>");
            if (textFrame) {
                textFrame.contents = firstWord;
            } else {
                alert("Text frame not found on layer: Name<Radial Repeat>");
                break;
            }

            // Export to SVG
            var saveFilePath = "~/Desktop/exports/" + firstWord + ".svg"; // <-- change export folder if needed
            exportToSVG(saveFilePath);
        }
        alert("SVG export complete!");
    }
}
