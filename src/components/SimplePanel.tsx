import React, { useState } from 'react';
import { ClipLoader } from 'react-spinners';
import ReactMarkdown from 'react-markdown';
import { PanelProps } from '@grafana/data';
import { SimpleOptions } from 'types';
import { css, cx } from '@emotion/css';
import { useStyles2} from '@grafana/ui';
import html2canvas from 'html2canvas';

interface Props extends PanelProps<SimpleOptions> {}

const getStyles = () => {
  return {
    wrapper: css`
      display: flex;
      flex-direction: column;
    `,
    options: css`
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      gap: 10px;
    `,
    selectInput: css`
      max-width: 130px;
      height: 23px;
    `,
    checkbox: css`
      margin-right: 10px;
    `,
    outputText: css`
      width: 100%;
      flex: 1;
      overflow-y: auto;

      h3 {
        font-size: 1em;
      }

      ul {
        margin-bottom: 10px;
      }
    `,
    svg: css`
      position: absolute;
      top: 0;
      left: 0;
    `,
    textBox: css`
      position: absolute;
      bottom: 0;
      left: 0;
      padding: 10px;
    `,
  };
};

const analysisOptions: { [key: string]: string }= {
  Summary: `This dashboard shows an overview of an S&P 500 stock's price movements. The first panel presents a line chart of the stock’s closing price, while the second panel visualizes price fluctuations using a candlestick chart. The date range is displayed in the top right. Summarize the key takeaways, emphasizing significant trends or movements without excessive detail.`,
  Insights: `This dashboard shows the price evolution of an S&P 500 stock. The first panel presents a line chart of closing prices, and the second panel uses candlesticks to depict price movements over time. The date range is in the top right. Analyze the data, identifying key trends, patterns, or anomalies. Provide insights into market behavior, potential drivers, and any notable fluctuations.`,
  Accessibility: `This dashboard shows stock price trends, including a line chart for closing prices and a candlestick chart for price variations. The date range is in the top right. Describe the charts in detail for visually impaired users, explaining the axes, data points, and any patterns or significant changes. Ensure a clear and thorough explanation of what the data conveys`,
  Diagnosis: `This dashboard shows stock price movements, with a line chart for closing prices and a candlestick chart for price fluctuations. The date range is in the top right. Identify any irregularities, potential issues, or correlations in the data. Highlight anomalies, inconsistencies, or trends that may indicate risks, inefficiencies, or underlying market conditions.`,
  Comparison: `This dashboard shows stock price data, including a line chart for closing prices and a candlestick chart for price movements over time. The date range is in the top right. Compare the two panels, identifying correlations, discrepancies, or significant differences in how each visualization represents price trends. Highlight key insights from this comparison.`,
  Forecasting: `This dashboard shows stock price trends, with a line chart of closing prices and a candlestick chart depicting price movements. The date range is in the top right. Based on the current data, predict potential future trends. Identify patterns that may suggest upcoming fluctuations, and explain the reasoning behind your forecast.`
};

export const SimplePanel: React.FC<Props> = ({ options, data, width, height, fieldConfig, id }) => {  
  const styles = useStyles2(getStyles);
  
  const [buttonText, setButtonText] = useState('Analyse');
  const [buttonEnabled, setButtonEnabled] = useState(true);
  const [analysisText, setAnalysisText] = useState('Please choose an analysis option and click Analyse.');
  
  const [selectedOption, setSelectedOption] = useState('');
  const [prompt, setPrompt] = useState(analysisOptions.Summary);

  const [showSpinner, setShowSpinner] = useState(false);

  const handleOptionChange = (event: any) => {  
    const selected = event.target.value;
    setSelectedOption(selected);
    setPrompt(analysisOptions[selected]);
  };

  const onButtonClick = async () => {
    try {
      setButtonText('Analysing...');
      setButtonEnabled(false);
      setShowSpinner(true);

      const elementToIgnore = document.querySelector('[data-testid="data-testid Panel header Chart Analyzer"]');

      if (elementToIgnore instanceof HTMLElement) {
        elementToIgnore.style.display = 'none'; // Ocultar antes de la captura
      }
  
      const canvas = await html2canvas(document.body, { useCORS: true, logging: false });
      let dataUrl = canvas.toDataURL("image/png");
      const base64Image = dataUrl.replace(/^data:image\/png;base64,/, "");  
      if (elementToIgnore instanceof HTMLElement) {
        elementToIgnore.style.display = 'flex'; 
      }
      const match = options.Address.match(/(?:https?:\/\/)?(?:localhost:\d+\/)?(.+)/);

      if (match) {
        const response = await fetch(`http://${match[1]}/api/generate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: options.Model,
            prompt: prompt,
            stream: false,
            images: [base64Image],
          })
        });
        const text = await response.text(); // Obtiene la respuesta como texto
        console.log("Raw response:", text);
        try {
          const data = JSON.parse(text);
          console.log("Parsed JSON:", data);
          const responseData = data
          setAnalysisText(responseData.response || 'Error processing response');
    
          setButtonText('Analyse');
          setButtonEnabled(true);
          setShowSpinner(false);
        } catch (error) {
          console.error("Error parsing JSON:", error);
        }
      }
    } catch (err) {
      console.error(err);
    }
  };
  

  return (
    <div className={cx(styles.wrapper, css`
      width: ${width}px;
      height: ${height}px;
    `)}>
      <div className={cx(styles.options)}>
        <select id="analysisType" value={selectedOption} onChange={handleOptionChange} className={cx(styles.selectInput)}>
          {Object.keys(analysisOptions).map(option => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
        {showSpinner && <ClipLoader color="#36d7b7" size={35} />}
        <button onClick={onButtonClick} disabled={!buttonEnabled}>{buttonText}</button>
      </div>
      {analysisText && (
        <div className={cx(styles.outputText)}>
          <ReactMarkdown>{analysisText}</ReactMarkdown>
        </div>
      )}
    </div>
  );
  
};
