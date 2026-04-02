import { useState, useCallback, useRef, useEffect } from "react";

const SPRITE_COLORS = ["transparent","#5C3A4E","#E85D75","#FF9EAE","#2D5016","#FFD700","#6B8E23","#D4A017","#D4698A","#FFB6C1","#FFDAB9","#C44569","#FFFFFF","#E8A87C","#87CEEB","#2A1F3D","#FF6B8A","#DA70D6","#F5F0E1"];
const SPRITE_DATA = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,2,3,2,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,2,3,1,4,5,2,3,2,5,4,2,3,5,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,6,2,2,1,6,5,2,2,2,5,6,2,2,5,6,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,5,5,5,5,5,3,5,5,5,5,5,5,3,5,5,5,5,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,7,7,7,7,3,7,7,7,7,7,7,3,7,7,7,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,8,9,9,8,9,3,8,9,9,8,9,9,3,9,9,8,9,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,1,9,8,9,9,8,9,3,8,9,9,8,9,9,3,9,9,8,9,9,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,1,9,9,9,9,9,9,9,3,9,9,10,9,9,9,3,9,9,9,9,9,9,1,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,1,9,9,9,9,9,9,10,3,10,10,10,10,10,10,3,9,9,9,9,9,9,1,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,1,8,9,9,9,9,9,10,10,3,10,10,10,10,10,10,3,10,9,9,9,9,9,8,1,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,1,8,9,9,9,11,10,10,10,3,10,10,10,10,10,10,3,10,10,11,9,9,9,8,1,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,1,8,8,9,9,9,10,10,10,10,3,10,10,10,10,10,10,3,10,10,10,9,9,9,8,8,1,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,1,8,8,9,9,10,10,10,10,10,3,10,10,10,10,10,10,3,10,10,10,10,9,9,8,8,1,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,1,8,8,9,9,10,10,12,12,12,3,10,10,10,10,10,10,3,12,12,10,10,9,9,8,8,1,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,1,8,8,9,13,10,12,14,15,12,3,10,10,10,10,10,12,3,15,12,12,10,13,9,8,8,1,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,1,8,8,9,13,10,12,14,15,14,12,10,10,10,10,10,12,14,15,14,12,10,13,9,8,8,1,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,1,8,8,8,9,13,10,12,14,14,14,12,10,10,10,10,10,12,14,14,14,12,10,13,9,8,8,8,1,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,1,8,8,9,13,10,16,12,12,12,10,10,10,10,10,10,10,12,12,12,16,10,13,9,8,8,1,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,1,1,1,1,8,8,13,13,16,16,16,10,10,10,10,10,10,10,10,10,10,10,16,16,16,13,13,8,8,1,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,1,1,11,11,11,1,8,8,9,16,16,16,16,16,10,10,10,13,13,10,10,10,10,16,16,16,16,16,9,8,8,1,1,1,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,11,11,11,11,11,1,8,8,9,13,16,16,16,10,10,10,10,10,10,10,10,10,10,10,16,16,16,13,9,8,8,1,11,11,1,0,0,0,0,0,0,0,0],[0,0,0,1,11,11,11,11,11,11,1,8,8,9,13,10,16,10,10,10,10,10,10,10,10,10,10,10,10,10,16,10,13,9,8,8,1,11,11,11,1,0,0,0,0,0,0,0],[0,0,0,1,11,11,11,11,11,11,11,1,8,9,13,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,13,9,8,1,11,11,11,11,11,1,0,0,0,0,0,0],[0,0,1,11,11,11,11,2,2,2,2,1,8,9,9,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,9,9,8,1,2,2,11,11,11,1,0,0,0,0,0,0],[0,0,1,11,11,11,2,2,2,2,2,2,1,9,9,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,9,9,1,2,2,2,2,11,11,11,1,0,0,0,0,0],[0,0,1,11,11,11,17,17,17,17,17,17,1,9,9,9,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,9,9,9,1,17,17,17,17,17,11,11,1,0,0,0,0,0],[0,0,1,11,11,11,2,2,2,17,2,2,2,1,9,9,9,10,10,10,10,10,10,10,10,10,10,10,10,10,9,9,9,1,2,2,3,2,2,2,11,11,11,1,0,0,0,0],[0,0,1,11,11,11,2,2,17,17,3,3,2,2,1,9,9,9,10,10,10,10,10,10,10,10,10,10,10,9,9,9,1,2,2,3,3,3,17,2,2,11,11,1,0,0,0,0],[0,0,1,11,11,11,17,17,17,17,17,17,17,17,2,1,9,9,9,10,10,10,10,10,10,10,10,10,9,9,9,1,11,2,17,17,17,17,17,17,17,17,11,11,1,0,0,0],[0,0,0,1,11,11,2,2,17,17,3,3,3,2,2,11,1,9,9,9,13,10,10,10,10,10,13,9,9,9,1,11,11,2,2,3,3,3,17,17,2,2,11,11,1,0,0,0],[0,0,0,1,11,11,2,2,2,17,3,3,3,2,2,11,11,1,1,9,13,10,10,10,10,10,13,9,1,1,1,11,11,2,2,2,3,3,17,17,2,2,11,11,11,1,0,0],[0,0,0,0,1,11,11,17,17,17,17,17,17,17,2,11,11,1,3,3,3,18,2,18,2,18,3,3,3,1,0,1,11,11,17,17,17,17,17,17,17,17,11,11,11,1,0,0],[0,0,0,0,1,11,11,11,2,2,2,3,2,2,2,11,1,3,3,3,18,18,18,2,18,18,18,3,3,3,1,1,11,11,11,2,2,2,17,2,2,2,11,11,11,1,0,0],[0,0,0,0,0,1,11,11,2,2,2,2,2,2,2,1,3,3,3,18,18,18,2,18,2,18,18,18,3,3,3,1,1,11,11,2,2,2,2,2,2,2,11,11,11,1,0,0],[0,0,0,0,0,1,11,11,11,17,17,17,17,17,1,3,3,3,18,18,18,18,18,18,18,18,18,18,18,3,3,3,1,11,11,11,17,17,17,17,17,17,11,11,11,1,0,0],[0,0,0,0,0,0,1,11,11,11,2,2,2,1,3,3,3,18,18,18,18,18,18,18,18,18,18,18,18,18,3,3,3,1,11,11,11,2,2,2,2,11,11,11,11,1,0,0],[0,0,0,0,0,0,1,11,11,11,11,11,1,3,3,3,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,3,3,3,1,11,11,11,11,11,11,11,11,11,1,0,0,0],[0,0,0,0,0,0,0,1,11,11,11,1,3,3,3,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,3,3,3,1,11,11,11,11,11,11,11,11,1,0,0,0],[0,0,0,0,0,0,0,0,1,11,1,3,3,3,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,18,3,3,3,1,11,11,11,11,11,11,1,0,0,0,0],[0,0,0,0,0,0,0,0,0,1,1,11,11,11,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1,11,11,11,1,1,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]];

function decodeSprite(t, d) { return d.map(function(r) { return r.map(function(i) { return t[i]; }); }); }

var DEFAULT_PALETTE = ["#000000","#1D2B53","#7E2553","#008751","#AB5236","#5F574F","#C2C3C7","#FFF1E8","#FF004D","#FFA300","#FFEC27","#00E436","#29ADFF","#83769C","#FF77A8","#FFCCAA"];
var GAME_PALETTE = [
  {hex:"#E85D75",name:"Rose Fairy"},{hex:"#5B9BD5",name:"Lilypad Fairy"},
  {hex:"#6B8E23",name:"Fern Fairy"},{hex:"#9B59B6",name:"Mushroom Fairy"},
  {hex:"#D4A017",name:"Nectar"},{hex:"#87CEEB",name:"Dewshine"},
  {hex:"#8B4513",name:"Heartwood"},{hex:"#DA70D6",name:"Shimmer"},
  {hex:"#FFD700",name:"Coins"},{hex:"#F5F0E1",name:"Background"},
  {hex:"#2D5016",name:"Forest Green"},{hex:"#7B2D8E",name:"Magic Purple"}
];
var TR = "transparent";

function floodFill(grid, row, col, target, fill, rows, cols) {
  if (target === fill) return grid;
  var g = grid.map(function(r) { return r.slice(); });
  var s = [[row, col]];
  while (s.length) {
    var p = s.pop(), r = p[0], c = p[1];
    if (r < 0 || r >= rows || c < 0 || c >= cols || g[r][c] !== target) continue;
    g[r][c] = fill;
    s.push([r-1,c],[r+1,c],[r,c-1],[r,c+1]);
  }
  return g;
}

function makeChecker(ctx, sz) {
  var c = document.createElement("canvas");
  c.width = sz * 2; c.height = sz * 2;
  var x = c.getContext("2d");
  x.fillStyle = "#e0e0e0"; x.fillRect(0,0,sz*2,sz*2);
  x.fillStyle = "#ccc"; x.fillRect(0,0,sz,sz); x.fillRect(sz,sz,sz,sz);
  return ctx.createPattern(c, "repeat");
}

export default function PixelArtEditor() {
  var _rows = useState(48), rows = _rows[0], setRows = _rows[1];
  var _cols = useState(48), cols = _cols[0], setCols = _cols[1];
  var _grid = useState(function() { return decodeSprite(SPRITE_COLORS, SPRITE_DATA); }), grid = _grid[0], setGrid = _grid[1];
  var _color = useState("#000000"), color = _color[0], setColor = _color[1];
  var _tool = useState("draw"), tool = _tool[0], setTool = _tool[1];
  var _sg = useState(true), showGrid = _sg[0], setShowGrid = _sg[1];
  var _hist = useState([]), history = _hist[0], setHistory = _hist[1];
  var _redo = useState([]), redoStack = _redo[0], setRedoStack = _redo[1];
  var _draw = useState(false), isDrawing = _draw[0], setIsDrawing = _draw[1];
  var _scale = useState(1), pngScale = _scale[0], setPngScale = _scale[1];
  var _ir = useState("48"), inputRows = _ir[0], setInputRows = _ir[1];
  var _ic = useState("48"), inputCols = _ic[0], setInputCols = _ic[1];
  var _cc = useState(["#5C3A4E","#FF9EAE","#D4698A","#FFB6C1","#FFDAB9","#C44569","#FFFFFF","#E8A87C","#2A1F3D","#FF6B8A"]), customColors = _cc[0], setCustomColors = _cc[1];
  var _fn = useState("rose_portrait"), fileName = _fn[0], setFileName = _fn[1];
  var canvasRef = useRef(null);
  var gridRef = useRef(grid);
  var checkerRef = useRef(null);
  gridRef.current = grid;

  var cellSize = Math.max(2, Math.floor(480 / Math.max(rows, cols)));
  var canvasW = cellSize * cols;
  var canvasH = cellSize * rows;

  useEffect(function() {
    var canvas = canvasRef.current;
    if (!canvas) return;
    var ctx = canvas.getContext("2d");
    ctx.imageSmoothingEnabled = false;
    if (!checkerRef.current) checkerRef.current = makeChecker(ctx, Math.max(4, Math.floor(cellSize/2)));
    ctx.fillStyle = checkerRef.current;
    ctx.fillRect(0, 0, canvasW, canvasH);
    for (var r = 0; r < rows; r++) {
      for (var c = 0; c < cols; c++) {
        var clr = grid[r] && grid[r][c];
        if (clr && clr !== TR) { ctx.fillStyle = clr; ctx.fillRect(c*cellSize, r*cellSize, cellSize, cellSize); }
      }
    }
    if (showGrid) {
      ctx.strokeStyle = "rgba(255,255,255,0.12)"; ctx.lineWidth = 1;
      for (var i = 0; i <= cols; i++) { ctx.beginPath(); ctx.moveTo(i*cellSize+0.5,0); ctx.lineTo(i*cellSize+0.5,canvasH); ctx.stroke(); }
      for (var j = 0; j <= rows; j++) { ctx.beginPath(); ctx.moveTo(0,j*cellSize+0.5); ctx.lineTo(canvasW,j*cellSize+0.5); ctx.stroke(); }
    }
  }, [grid, showGrid, rows, cols, cellSize, canvasW, canvasH]);

  var pushHistory = useCallback(function(g) {
    setHistory(function(h) { return h.slice(-30).concat([g.map(function(r){return r.slice();})]); });
    setRedoStack([]);
  }, []);

  var undo = useCallback(function() {
    if (!history.length) return;
    setRedoStack(function(rs) { return rs.concat([gridRef.current.map(function(r){return r.slice();})]); });
    setGrid(history[history.length - 1]);
    setHistory(function(h) { return h.slice(0, -1); });
  }, [history]);

  var redo2 = useCallback(function() {
    if (!redoStack.length) return;
    setHistory(function(h) { return h.concat([gridRef.current.map(function(r){return r.slice();})]); });
    setGrid(redoStack[redoStack.length - 1]);
    setRedoStack(function(rs) { return rs.slice(0, -1); });
  }, [redoStack]);

  useEffect(function() {
    var handler = function(e) {
      if ((e.metaKey || e.ctrlKey) && e.key === "z") { e.preventDefault(); e.shiftKey ? redo2() : undo(); }
    };
    window.addEventListener("keydown", handler);
    return function() { window.removeEventListener("keydown", handler); };
  }, [undo, redo2]);

  var paint = useCallback(function(r, c, isNew) {
    if (r < 0 || r >= rows || c < 0 || c >= cols) return;
    setGrid(function(prev) {
      if (isNew) pushHistory(prev);
      if (tool === "fill") return floodFill(prev, r, c, prev[r][c], color, rows, cols);
      if (tool === "erase") {
        if (prev[r][c] === TR) return prev;
        var g = prev.map(function(row){return row.slice();}); g[r][c] = TR; return g;
      }
      if (tool === "pick") { if (prev[r][c] !== TR) setColor(prev[r][c]); return prev; }
      if (prev[r][c] === color) return prev;
      var g2 = prev.map(function(row){return row.slice();}); g2[r][c] = color; return g2;
    });
  }, [tool, color, rows, cols, pushHistory]);

  var getCell = function(e) {
    var rect = canvasRef.current && canvasRef.current.getBoundingClientRect();
    if (!rect) return null;
    var px = e.touches ? e.touches[0].clientX : e.clientX;
    var py = e.touches ? e.touches[0].clientY : e.clientY;
    var c2 = Math.floor((px - rect.left) / (rect.width / cols));
    var r2 = Math.floor((py - rect.top) / (rect.height / rows));
    return (r2 >= 0 && r2 < rows && c2 >= 0 && c2 < cols) ? [r2, c2] : null;
  };

  var onDown = function(e) { e.preventDefault(); setIsDrawing(true); var c2 = getCell(e); if (c2) paint(c2[0],c2[1],true); };
  var onMove = function(e) { if (!isDrawing) return; e.preventDefault(); var c2 = getCell(e); if (c2) paint(c2[0],c2[1]); };
  var onUp = function() { setIsDrawing(false); };

  var resizeGrid = function() {
    var nr = Math.max(1, Math.min(128, parseInt(inputRows) || rows));
    var nc = Math.max(1, Math.min(128, parseInt(inputCols) || cols));
    setInputRows(String(nr)); setInputCols(String(nc));
    if (nr === rows && nc === cols) return;
    pushHistory(grid); checkerRef.current = null;
    setGrid(Array.from({length:nr}, function(_,r) { return Array.from({length:nc}, function(_,c) { return r<rows&&c<cols ? grid[r][c] : TR; }); }));
    setRows(nr); setCols(nc);
  };

  var clearGrid = function() { pushHistory(grid); setGrid(Array.from({length:rows}, function(){return Array(cols).fill(TR);})); };

  var downloadPNG = function() {
    try {
      var cv = document.createElement("canvas");
      cv.width = cols*pngScale; cv.height = rows*pngScale;
      var x = cv.getContext("2d"); x.imageSmoothingEnabled = false;
      for (var r=0;r<rows;r++) for (var c=0;c<cols;c++) {
        if (grid[r][c] !== TR) { x.fillStyle = grid[r][c]; x.fillRect(c*pngScale,r*pngScale,pngScale,pngScale); }
      }
      cv.toBlob(function(blob) {
        if (!blob) return;
        var u = URL.createObjectURL(blob);
        var a = document.createElement("a"); a.href = u; a.download = fileName + ".png";
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
        setTimeout(function() { URL.revokeObjectURL(u); }, 200);
      }, "image/png");
    } catch(err) { console.error("Export failed", err); }
  };

  var addCustomColor = function() {
    if (customColors.indexOf(color) === -1 && DEFAULT_PALETTE.indexOf(color) === -1) {
      setCustomColors(function(cc) { return cc.concat([color]); });
    }
  };

  var panel = { background:"#16213e", border:"2px solid #0f3460", borderRadius:"4px", padding:"8px" };
  var btnS = { background:"#0f3460", border:"1px solid #1a3a6e", color:"#e0e0e0", padding:"5px 8px", borderRadius:"3px", cursor:"pointer", fontFamily:"inherit", fontSize:"8px", textTransform:"uppercase", letterSpacing:"0.5px" };
  var inpS = { background:"#0f3460", border:"1px solid #1a3a6e", color:"#e0e0e0", padding:"4px 6px", borderRadius:"3px", fontFamily:"inherit", fontSize:"9px", boxSizing:"border-box" };

  var mkSwatch = function(c, active) {
    return { width:"20px", height:"20px", background: c===TR ? "repeating-conic-gradient(#ccc 0% 25%, #fff 0% 50%) 50%/10px 10px" : c, border: active ? "2px solid #ffa300" : "1px solid #333", borderRadius:"2px", cursor:"pointer", boxSizing:"border-box" };
  };

  var toolDefs = [{id:"draw",label:"\u270F\uFE0F",t:"Draw"},{id:"erase",label:"\uD83E\uDDF9",t:"Erase"},{id:"fill",label:"\uD83E\uDEA3",t:"Fill"},{id:"pick",label:"\uD83D\uDC89",t:"Pick"}];

  return (
    <div style={{fontFamily:"'Press Start 2P','Courier New',monospace",background:"#1a1a2e",color:"#e0e0e0",minHeight:"100vh",display:"flex",flexDirection:"column",alignItems:"center",padding:"12px",boxSizing:"border-box",userSelect:"none"}}>
      <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet" />
      <div style={{fontSize:"11px",letterSpacing:"2px",color:"#ffa300",marginBottom:"10px",textTransform:"uppercase"}}>Pixel Forge</div>
      <div style={{display:"flex",gap:"14px",flexWrap:"wrap",justifyContent:"center",width:"100%",maxWidth:"760px"}}>
        <div style={{display:"flex",flexDirection:"column",gap:"10px",minWidth:"160px",fontSize:"9px"}}>
          <div style={panel}>
            <div style={{fontSize:"8px",color:"#29adff",marginBottom:"6px",textTransform:"uppercase",letterSpacing:"1px"}}>Tools</div>
            <div style={{display:"flex",gap:"4px",flexWrap:"wrap"}}>
              {toolDefs.map(function(td) { return <button key={td.id} title={td.t} onClick={function(){setTool(td.id);}} style={{width:"36px",height:"36px",border:tool===td.id?"2px solid #ffa300":"2px solid #0f3460",borderRadius:"4px",background:tool===td.id?"#0f3460":"#1a1a2e",cursor:"pointer",fontSize:"16px",display:"flex",alignItems:"center",justifyContent:"center"}}>{td.label}</button>; })}
            </div>
          </div>
          <div style={panel}>
            <div style={{fontSize:"8px",color:"#29adff",marginBottom:"6px",textTransform:"uppercase",letterSpacing:"1px"}}>Color</div>
            <div style={{display:"flex",gap:"6px",alignItems:"center",marginBottom:"6px"}}>
              <div style={{width:"32px",height:"32px",background:color===TR?"repeating-conic-gradient(#ccc 0% 25%, #fff 0% 50%) 50%/10px 10px":color,border:"2px solid #ffa300",borderRadius:"3px"}} />
              <input type="color" value={color===TR?"#ffffff":color} onChange={function(e){setColor(e.target.value);}} style={{width:"32px",height:"32px",padding:0,border:"none",cursor:"pointer",background:"transparent"}} />
              <button style={btnS} onClick={addCustomColor} title="Save color">+</button>
            </div>
            <div style={{display:"flex",flexWrap:"wrap",gap:"3px"}}>
              <div style={mkSwatch(TR,color===TR)} onClick={function(){setColor(TR);}} title="Transparent" />
              {DEFAULT_PALETTE.map(function(c){return <div key={c} style={mkSwatch(c,color===c)} onClick={function(){setColor(c);}} title={c} />;})}
              {customColors.map(function(c){return <div key={c} style={mkSwatch(c,color===c)} onClick={function(){setColor(c);}} title={c} />;})}
            </div>
            <div style={{fontSize:"8px",color:"#00e436",marginTop:"8px",marginBottom:"6px",textTransform:"uppercase",letterSpacing:"1px"}}>Game Palette</div>
            <div style={{display:"flex",flexWrap:"wrap",gap:"3px"}}>
              {GAME_PALETTE.map(function(c){return <div key={c.hex} style={mkSwatch(c.hex,color===c.hex)} onClick={function(){setColor(c.hex);}} title={c.name+" ("+c.hex+")"} />;})}
            </div>
          </div>
          <div style={panel}>
            <div style={{fontSize:"8px",color:"#29adff",marginBottom:"6px",textTransform:"uppercase",letterSpacing:"1px"}}>Canvas</div>
            <div style={{display:"flex",gap:"4px",alignItems:"center",marginBottom:"6px"}}>
              <input style={Object.assign({},inpS,{width:"44px"})} value={inputCols} onChange={function(e){setInputCols(e.target.value);}} />
              <span style={{color:"#555",fontSize:"9px"}}>{"\u00D7"}</span>
              <input style={Object.assign({},inpS,{width:"44px"})} value={inputRows} onChange={function(e){setInputRows(e.target.value);}} />
              <button style={btnS} onClick={resizeGrid}>Set</button>
            </div>
            <div style={{display:"flex",gap:"4px"}}>
              <button style={btnS} onClick={clearGrid}>Clear</button>
              <button style={btnS} onClick={undo} disabled={!history.length}>Undo</button>
              <button style={btnS} onClick={redo2} disabled={!redoStack.length}>Redo</button>
            </div>
            <label style={{display:"flex",alignItems:"center",gap:"6px",marginTop:"6px",cursor:"pointer",fontSize:"8px"}}>
              <input type="checkbox" checked={showGrid} onChange={function(e){setShowGrid(e.target.checked);}} /> Grid lines
            </label>
          </div>
          <div style={panel}>
            <div style={{fontSize:"8px",color:"#29adff",marginBottom:"6px",textTransform:"uppercase",letterSpacing:"1px"}}>Export</div>
            <div style={{marginBottom:"6px"}}><input style={Object.assign({},inpS,{width:"100%"})} value={fileName} onChange={function(e){setFileName(e.target.value);}} placeholder="filename" /></div>
            <div style={{display:"flex",gap:"4px",alignItems:"center",marginBottom:"6px"}}>
              <span style={{fontSize:"8px",whiteSpace:"nowrap"}}>PNG scale:</span>
              <input style={Object.assign({},inpS,{width:"40px"})} type="number" min={1} max={32} value={pngScale} onChange={function(e){setPngScale(Math.max(1,Math.min(32,parseInt(e.target.value)||1)));}} />
              <span style={{fontSize:"7px",color:"#888"}}>{(cols*pngScale)+"\u00D7"+(rows*pngScale)+"px"}</span>
            </div>
            <button style={{background:"#008751",border:"1px solid #00a566",color:"#fff",padding:"7px 10px",borderRadius:"3px",cursor:"pointer",fontFamily:"inherit",fontSize:"8px",textTransform:"uppercase",letterSpacing:"0.5px",width:"100%",boxSizing:"border-box"}} onClick={downloadPNG}>Download PNG</button>
          </div>
        </div>
        <div style={{display:"flex",flexDirection:"column",alignItems:"center",gap:"6px"}}>
          <canvas ref={canvasRef} width={canvasW} height={canvasH}
            style={{width:canvasW,height:canvasH,border:"2px solid #0f3460",cursor:tool==="pick"?"crosshair":tool==="fill"?"cell":"pointer",touchAction:"none",imageRendering:"pixelated"}}
            onMouseDown={onDown} onMouseMove={onMove} onMouseUp={onUp} onMouseLeave={onUp}
            onTouchStart={onDown} onTouchMove={onMove} onTouchEnd={onUp} />
          <div style={{fontSize:"7px",color:"#555"}}>{cols+"\u00D7"+rows+" \u2022 "+tool+" \u2022 "+(color===TR?"transparent":color)}</div>
        </div>
      </div>
    </div>
  );
}
