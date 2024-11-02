import { BaseDatabaseObject, convertToBaseDatabaseObject, convertToEmbeddable, Embeddable, EnhancedComponentProps } from "./CollectionTypes";
import { References } from "./ReferenceTypes";

export interface ExecutionHistoryItem {
    parent_task_id?: string;
    node_name: string;
    execution_order: number;
    exit_code?: number;
}

export interface NodeResponse extends ExecutionHistoryItem {
    references: References;
}

export interface TaskResponse extends BaseDatabaseObject, Embeddable {
    task_name: string;
    task_id: string;
    task_description: string;
    status: 'pending' | 'complete' | 'failed';
    result_code: number;
    task_outputs?: string; 
    task_inputs?: { [key: string]: any };
    result_diagnostic?: string;
    usage_metrics?: { [key: string]: any };
    execution_history?: ExecutionHistoryItem[];
    node_references?: NodeResponse[];
}

export const convertToTaskResponse = (data: any): TaskResponse => {
    return {
        ...convertToBaseDatabaseObject(data),
        ...convertToEmbeddable(data),
        task_name: data?.task_name || '',
        task_description: data?.task_description || '',
        task_id: data?.task_id || '',
        status: data?.status || 'pending',
        result_code: data?.result_code || 0,
        task_outputs: data?.task_outputs || {},
        task_inputs: data?.task_inputs || {},
        result_diagnostic: data?.result_diagnostic || '',
        usage_metrics: data?.usage_metrics || {},
        execution_history: data?.execution_history || [],
        node_references: data?.node_references || [],
    };
};

export interface TaskResponseComponentProps extends EnhancedComponentProps<TaskResponse> {
    
}