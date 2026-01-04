import React from 'react';
import Plot from 'react-plotly.js';
import { StockCandle } from '../types';

interface Props {
  data: StockCandle[];
  pivotPrice?: number;
  stopLoss?: number;
}

export const CandlestickChart: React.FC<Props> = ({ data, pivotPrice, stopLoss }) => {
  if (!data || data.length === 0) return <div>No Data</div>;

  const dates = data.map(d => d.date);
  const open = data.map(d => d.open);
  const high = data.map(d => d.high);
  const low = data.map(d => d.low);
  const close = data.map(d => d.close);
  const volume = data.map(d => d.volume);
  const ma10 = data.map(d => d.ma10);
  const ma20 = data.map(d => d.ma20);
  const ma50 = data.map(d => d.ma50);

  // Volume Color Logic
  const volumeColors = data.map(d => {
    const isUp = d.close >= d.open;
    // Highlight spike: Volume > 1.5x 50-day Avg Vol AND Price Up
    if (d.volMa50 && d.volume > d.volMa50 * 1.5 && isUp) {
      return '#facc15'; // Bright Gold
    }
    return isUp ? '#ef4444' : '#22c55e';
  });

  const shapes: any[] = [];

  // Pivot Line (White Dashed)
  if (pivotPrice) {
    shapes.push({
      type: 'line',
      xref: 'x',
      yref: 'y',
      x0: dates[0],
      y0: pivotPrice,
      x1: dates[dates.length - 1],
      y1: pivotPrice,
      line: {
        color: 'white',
        width: 1,
        dash: 'dash'
      },
      label: {
        text: 'Pivot',
        textposition: 'end',
        font: { color: 'white', size: 10 }
      }
    } as any); // cast any due to partial typing in react-plotly wrapper
  }

  // Stop Loss Area (Red Transparent)
  if (pivotPrice && stopLoss) {
    shapes.push({
      type: 'rect',
      xref: 'x',
      yref: 'y',
      x0: dates[0],
      y0: stopLoss,
      x1: dates[dates.length - 1],
      y1: pivotPrice,
      fillcolor: '#ef4444',
      opacity: 0.1,
      line: {
        width: 0
      }
    });
  }

  return (
    <div className="w-full h-[500px] bg-slate-900 rounded-lg p-2 border border-slate-700">
      <Plot
        data={[
          // Candlestick Trace
          {
            x: dates,
            open: open,
            high: high,
            low: low,
            close: close,
            type: 'candlestick',
            name: 'Price',
            xaxis: 'x',
            yaxis: 'y',
            increasing: { line: { color: '#ef4444', width: 1 } },
            decreasing: { line: { color: '#22c55e', width: 1 } }
          },
          // MAs
          {
            x: dates,
            y: ma10 as number[],
            type: 'scatter',
            mode: 'lines',
            name: '10MA',
            line: { color: '#fbbf24', width: 1 }, // Yellow/Orange
            xaxis: 'x',
            yaxis: 'y',
            hoverinfo: 'skip'
          },
          {
            x: dates,
            y: ma20 as number[],
            type: 'scatter',
            mode: 'lines',
            name: '20MA',
            line: { color: '#c084fc', width: 1 }, // Purple
            xaxis: 'x',
            yaxis: 'y',
            hoverinfo: 'skip'
          },
          {
            x: dates,
            y: ma50 as number[],
            type: 'scatter',
            mode: 'lines',
            name: '50MA',
            line: { color: '#22d3ee', width: 1.5 }, // Blue/Cyan
            xaxis: 'x',
            yaxis: 'y',
            hoverinfo: 'skip'
          },
          // Volume Trace
          {
            x: dates,
            y: volume,
            type: 'bar',
            name: 'Volume',
            marker: {
              color: volumeColors
            },
            xaxis: 'x', // Shared x-axis
            yaxis: 'y2', // Separate y-axis
            hoverinfo: 'y+name'
          }
        ]}
        layout={{
          autosize: true,
          grid: {
            rows: 2,
            columns: 1,
            roworder: 'top to bottom',
            pattern: 'independent' // independent axes
          },
          // Backgrounds
          paper_bgcolor: '#0f172a', // Slate 900
          plot_bgcolor: '#0f172a',
          
          // X Axis (Shared)
          xaxis: {
            autorange: true,
            domain: [0, 1], // Full width
            rangeslider: { visible: false }, // Remove range slider
            type: 'date',
            gridcolor: '#334155',
            linecolor: '#475569',
            tickfont: { color: '#94a3b8', size: 10 },
            anchor: 'y2' // Anchors to volume chart
          },
          
          // Y Axis 1 (Price) - Top 70%
          yaxis: {
            domain: [0.35, 1],
            autorange: true,
            type: 'linear',
            gridcolor: '#334155',
            linecolor: '#475569',
            tickfont: { color: '#94a3b8', size: 10 },
            side: 'right'
          },
          
          // Y Axis 2 (Volume) - Bottom 20%
          yaxis2: {
            domain: [0, 0.25],
            autorange: true,
            type: 'linear',
            gridcolor: '#334155',
            linecolor: '#475569',
            tickfont: { color: '#94a3b8', size: 10 },
            side: 'right'
          },

          shapes: shapes,

          // Interaction
          hovermode: 'x unified', // Crosshair
          showlegend: false,
          margin: { l: 10, r: 50, t: 30, b: 30 }, // Margins
          
          // Hover label styling
          hoverlabel: {
            bgcolor: '#1e293b',
            bordercolor: '#475569',
            font: { color: '#f8fafc' }
          }
        }}
        useResizeHandler={true}
        style={{ width: '100%', height: '100%' }}
        config={{ displayModeBar: false }}
      />
    </div>
  );
};