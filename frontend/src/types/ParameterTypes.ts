import { BaseDatabaseObject, convertToBaseDatabaseObject, convertToEmbeddable, EnhancedComponentProps } from "./CollectionTypes";
import { convertToUser } from "./UserTypes";

export interface FunctionParameters {
    type: "object";
    properties: { [key: string]: ParameterDefinition };
    required: string[];
}
export type ParameterTypes = "string" | "integer" | "boolean" | "object" | "array";
export interface ParameterDefinition extends BaseDatabaseObject {
    type: ParameterTypes;
    description: string;
    default?: any;
}
export const convertToParameterDefinition = (data: any): ParameterDefinition => {
    return {
        ...convertToBaseDatabaseObject(data),
        ...convertToEmbeddable(data),
        type: data?.type || '',
        description: data?.description || '',
        default: data?.default,
    };
};

export interface ParameterComponentProps extends EnhancedComponentProps<ParameterDefinition> {
}
export const getDefaultParameterForm = (): Partial<ParameterDefinition> => ({
    type: 'string',
    description: '',
    default: null
});


export interface FunctionConfig {
    name: string;
    description: string;
    parameters: FunctionParameters;
}

export interface ToolFunction {
    type: "function";
    function: FunctionConfig;
}

export interface ToolCallConfig {
    arguments: { [key: string]: any } | string;
    name: string;
}

export interface ToolCall {
    id?: string;
    type: "function";
    function: ToolCallConfig;
}

export type ToolParam = {
    name: string;
    description: string;
    input_schema: any;
};

export const convertToToolParam = (toolFunction: ToolFunction): ToolParam => {
    return {
        name: toolFunction.function.name,
        description: toolFunction.function.description,
        input_schema: toolFunction.function.parameters
    };
};

export const convertToFunctionConfig = (data: any): FunctionConfig => {
    return {
        name: data?.name || '',
        description: data?.description || '',
        parameters: data?.parameters || { type: "object", properties: {}, required: [] }
    };
};

export const convertToToolFunction = (data: any): ToolFunction => {
    return {
        type: "function",
        function: convertToFunctionConfig(data?.function)
    };
};

export const convertToToolCall = (data: any): ToolCall => {
    return {
        id: data?.id || undefined,
        type: "function",
        function: {
            arguments: data?.function?.arguments || {},
            name: data?.function?.name || ''
        }
    };
};
