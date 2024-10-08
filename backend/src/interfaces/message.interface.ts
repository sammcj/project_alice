import { Model, Types, Document } from 'mongoose';
import { IUserDocument } from "./user.interface";
import { References } from './references.interface';
import { FileType } from './file.interface';

export enum ContentType {
    TEXT = 'text',
    IMAGE = FileType.IMAGE,
    VIDEO = FileType.VIDEO,
    AUDIO = FileType.AUDIO,
    FILE = FileType.FILE,
    TASK_RESULT = 'task_result',
    MULTIPLE = 'multiple',
    URL_REFERENCE = 'url_reference'
}

export interface IMessage {
    content?: string;
    role: 'user' | 'assistant' | 'system' | 'tool';
    generated_by: 'user' | 'llm' | 'tool' | 'system';
    step: string;
    assistant_name?: string;
    context?: any;
    type: ContentType;
    tool_calls?: any[];
    tool_call_id?: string,
    request_type?: string | null;
    references?: References;
    creation_metadata?: Record<string, any>;
    created_by: Types.ObjectId | IUserDocument;
    updated_by: Types.ObjectId | IUserDocument;
}

export interface IMessageMethods {
    apiRepresentation(): any;
}

export interface IMessageDocument extends IMessage, Document, IMessageMethods {
    _id: Types.ObjectId; 
    createdAt: Date;
    updatedAt: Date;
}

export interface IMessageModel extends Model<IMessageDocument> {
    // Add any static methods here if needed
}