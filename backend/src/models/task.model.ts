import mongoose, { Schema } from 'mongoose';
import { functionParametersSchema } from '../utils/functionSchema';
import { ensureObjectIdForProperties } from '../utils/utils';
import { ITaskDocument, ITaskModel, TaskType } from '../interfaces/task.interface';
import { getObjectId } from '../utils/utils';
import { referencesSchema } from './reference.model';

const taskSchema = new Schema<ITaskDocument, ITaskModel>({
    task_name: { type: String, required: true },
    task_description: { type: String, required: true },
    task_type: { type: String, enum: Object.values(TaskType), required: true },
    input_variables: { type: functionParametersSchema },
    exit_codes: {
        type: Map,
        of: String,
        default: () => new Map([['0', 'Success'], ['1', 'Failed']])
    },
    recursive: { type: Boolean, default: true },
    templates: { type: Map, of: Schema.Types.ObjectId, ref: 'Prompt', default: null },
    tasks: { type: Map, of: Schema.Types.ObjectId, ref: 'Task', default: null },
    valid_languages: [String],
    exit_code_response_map: { type: Map, of: Number, default: null },
    start_node: { type: String, default: null },
    node_end_code_routing: { type: Map, of: Map, default: null },
    max_attempts: { type: Number, default: 1 },
    required_apis: { type: [String], default: null },
    agent: { type: Schema.Types.ObjectId, ref: 'Agent', default: null },
    user_checkpoints: { type: Map, of: Schema.Types.ObjectId, ref: 'UserCheckpoint', default: null },
    data_cluster: { type: referencesSchema, default: () => ({}) },
    created_by: { type: Schema.Types.ObjectId, ref: 'User' },
    updated_by: { type: Schema.Types.ObjectId, ref: 'User' }
}, { timestamps: true });

taskSchema.methods.apiRepresentation = function (this: ITaskDocument) {
    return {
        id: this._id,
        task_name: this.task_name || null,
        task_description: this.task_description || null,
        task_type: this.task_type || null,
        input_variables: this.input_variables || null,
        exit_codes: this.exit_codes ? Object.fromEntries(this.exit_codes) : {},
        recursive: this.recursive || false,
        templates: this.templates ? Object.fromEntries(this.templates) : null,
        tasks: this.tasks ? Object.fromEntries(this.tasks) : null,
        valid_languages: this.valid_languages || [],
        exit_code_response_map: this.exit_code_response_map ? Object.fromEntries(this.exit_code_response_map) : null,
        start_node: this.start_node || null,
        node_end_code_routing: this.node_end_code_routing ? Object.fromEntries(
            Array.from(this.node_end_code_routing.entries()).map(([key, value]) => [key, Object.fromEntries(value)])
        ) : null,
        max_attempts: this.max_attempts || 1,
        agent: this.agent ? (this.agent._id || this.agent) : null,
        created_by: this.created_by ? (this.created_by._id || this.created_by) : null,
        updated_by: this.updated_by ? (this.updated_by._id || this.updated_by) : null,
        createdAt: this.createdAt || null,
        updatedAt: this.updatedAt || null
    };
};

function ensureObjectIdForSave(this: ITaskDocument, next: mongoose.CallbackWithoutResultAndOptionalError) {
    this.agent = getObjectId(this.agent);
    this.created_by = getObjectId(this.created_by);
    this.updated_by = getObjectId(this.updated_by);

    if (this.templates) {
        for (const [key, value] of this.templates.entries()) {
            this.templates.set(key, getObjectId(value));
        }
    }
    if (this.tasks) {
        for (const [key, value] of this.tasks.entries()) {
            this.tasks.set(key, getObjectId(value));
        }
    }
    if (this.input_variables && this.input_variables.properties) {
        this.input_variables.properties = ensureObjectIdForProperties(this.input_variables.properties);
    }
    if (this.user_checkpoints) {
        for (const [key, value] of this.user_checkpoints.entries()) {
            this.user_checkpoints.set(key, getObjectId(value));
        }
    }
    next();
}

function ensureObjectIdForUpdate(this: mongoose.Query<any, any>, next: mongoose.CallbackWithoutResultAndOptionalError) {
    const update = this.getUpdate() as any;

    if (update.templates) {
        update.templates = Object.fromEntries(
            Object.entries(update.templates).map(([key, value]) => [key, getObjectId(value)])
        );
    }
    if (update.tasks) {
        update.tasks = Object.fromEntries(
            Object.entries(update.tasks).map(([key, value]) => [key, getObjectId(value)])
        );
    }
    if (update.user_checkpoints) {
        update.user_checkpoints = Object.fromEntries(
            Object.entries(update.user_checkpoints).map(([key, value]) => [key, getObjectId(value)])
        );
    }
    update.agent = getObjectId(update.agent);
    update.created_by = getObjectId(update.created_by);
    update.updated_by = getObjectId(update.updated_by);
    if (update && update.input_variables && update.input_variables.properties) {
        update.input_variables.properties = ensureObjectIdForProperties(update.input_variables.properties);
    }
    next();
}

function autoPopulate(this: mongoose.Query<any, any>, next: mongoose.CallbackWithoutResultAndOptionalError) {
    this.populate('created_by')
        .populate('updated_by')
        .populate('agent')

    this.populate({
        path: 'templates',
        options: { strictPopulate: false }
    });
    this.populate({
        path: 'tasks.$*',
        model: 'Task'
    });
    this.populate({
        path: 'user_checkpoints.$*',
        model: 'UserCheckpoint'
    });
    this.populate('input_variables.properties');
    next();
}

taskSchema.pre('save', ensureObjectIdForSave);
taskSchema.pre('findOneAndUpdate', ensureObjectIdForUpdate);
taskSchema.pre('find', autoPopulate);
taskSchema.pre('findOne', autoPopulate);

const Task = mongoose.model<ITaskDocument, ITaskModel>('Task', taskSchema);

export default Task;