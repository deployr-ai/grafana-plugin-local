import React, { useState } from 'react';
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
  Summary: `This image shows a Grafana Dashboard. Only focus on the panels on the dashboard. DO NOT INCLUDE the AI Analyser panel in your analysis. Provide a brief summary of what the dashboard is displaying, focusing on the most critical and relevant data points. Lighter colours on the heatmap indicate higher usage, darker colours indicate lower usage. Always start with "This dashboard shows..." and ensure that the summary captures the key insights without going into too much detail.`,
  Insights: `This image shows a Grafana Dashboard. Only focus on the panels on the dashboard. DO NOT INCLUDE the AI Analyser panel in your analysis. Please explain what the data is showing and share any insights you can gather from it. Lighter colours on the heatmap indicate higher usage, darker colours indicate lower usage. Always start with "This dashboard shows..." and provide detailed insights into the data presented, highlighting any trends, patterns, or anomalies you observe.`,
  Accessibility: `This image shows a Grafana Dashboard. Only focus on the panels on the dashboard. DO NOT INCLUDE the AI Analyser panel in your analysis. Please explain what the data is showing in great detail, aiming to provide a clear description for users who may be visually impaired. Describe each panel's content and structure comprehensively. Lighter colours on the heatmap indicate higher usage, darker colours indicate lower usage. Always start with "This dashboard shows..." and ensure that all aspects of the data are explained in a way that is accessible to all users.`,
  Diagnosis: `This image shows a Grafana Dashboard. Only focus on the panels on the dashboard. DO NOT INCLUDE the AI Analyser panel in your analysis. Please analyze the data for any potential issues or problems, highlighting correlations and any critical points of concern. Lighter colours on the heatmap indicate higher usage, darker colours indicate lower usage. Always start with "This dashboard shows..." and provide a detailed diagnosis of any potential issues or inefficiencies indicated by the data.`,
  Comparison: `This image shows a Grafana Dashboard. Only focus on the panels on the dashboard. DO NOT INCLUDE the AI Analyser panel in your analysis. Compare the data across different panels to highlight any correlations, discrepancies, or significant differences. Lighter colours on the heatmap indicate higher usage, darker colours indicate lower usage. Always start with "This dashboard shows..." and provide a comparative analysis, explaining how the data in various panels relate to each other.`,
  Forecasting: `This image shows a Grafana Dashboard. Only focus on the panels on the dashboard. DO NOT INCLUDE the AI Analyser panel in your analysis. Based on the current data, provide a forecast of future trends and usage patterns. Lighter colours on the heatmap indicate higher usage, darker colours indicate lower usage. Always start with "This dashboard shows..." and offer insights into what future data might look like, explaining the basis of your forecasts.`
};

export const SimplePanel: React.FC<Props> = ({ options, data, width, height, fieldConfig, id }) => {  
  const styles = useStyles2(getStyles);
  
  const [buttonText, setButtonText] = useState('Analyse');
  const [buttonEnabled, setButtonEnabled] = useState(true);
  const [analysisText, setAnalysisText] = useState('Please choose an analysis option and click Analyse.');
  
  const [selectedOption, setSelectedOption] = useState('');
  const [prompt, setPrompt] = useState(analysisOptions.Summary);

  const handleOptionChange = (event: any) => {
    const selected = event.target.value;
    setSelectedOption(selected);
    setPrompt(analysisOptions[selected]);
  };

  const onButtonClick = async () => {
    try {
      setButtonText('Analysing...');
      setButtonEnabled(false);
  
      const canvas = await html2canvas(document.body, { useCORS: true, logging: false });
      let dataUrl = canvas.toDataURL("image/png");
      const base64Image = dataUrl.replace(/^data:image\/png;base64,/, "");
      
      const response = await fetch(`${options.Address}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: options.Model,
          prompt: prompt,
          images: [base64Image],
          stream: false
        })
      });
      
      const responseData = await response.json();
      setAnalysisText(responseData.response || 'Error processing response');
  
      setButtonText('Analyse');
      setButtonEnabled(true);
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
