import React from 'react';
import { Box } from '@mui/material';
import PromptAgentTask from './PromptAgentTask';
import { TaskFormsProps } from '../../../../../types/TaskTypes';

const CodeGenerationLLMTask: React.FC<TaskFormsProps> = ({
  item, onChange, mode, handleAccordionToggle, activeAccordion, handleSave, apis
}) => {

  return (
    <Box>
      <PromptAgentTask
        apis={apis}
        items={null}
        handleSave={handleSave}
        item={item}
        onChange={onChange}
        mode={mode}
        handleAccordionToggle={handleAccordionToggle}
        activeAccordion={activeAccordion}
      />
    </Box>
  );
};

export default CodeGenerationLLMTask;