import mongoose, { CallbackWithoutResultAndOptionalError, Schema } from 'mongoose';
import { IDataClusterDocument, IDataClusterModel, References } from "../interfaces/references.interface";
import mongooseAutopopulate from 'mongoose-autopopulate';
import { ensureObjectIdHelper } from '../utils/utils';

export const referencesSchema = new Schema<References>({
    messages: [{ type: Schema.Types.ObjectId, ref: 'Message', autopopulate: true }],
    files: [{ type: Schema.Types.ObjectId, ref: 'FileReference', autopopulate: true }],
    task_responses: [{ type: Schema.Types.ObjectId, ref: 'TaskResult', autopopulate: true }],
    url_references: [{ type: Schema.Types.ObjectId, ref: 'URLReference', autopopulate: true }],
    string_outputs: [String],
    user_interactions: [{ type: Schema.Types.ObjectId, ref: 'UserInteraction', autopopulate: true }],
    embeddings: [{ type: Schema.Types.ObjectId, ref: 'EmbeddingChunk', autopopulate: true }],
});

function ensureObjectIdForSave(this: IDataClusterDocument, next: CallbackWithoutResultAndOptionalError) {
    if (this.messages) {
        this.messages = this.messages.map((obj) => ensureObjectIdHelper(obj));
    }
    if (this.files) {
        this.files = this.files.map((obj) => ensureObjectIdHelper(obj));
    }
    if (this.task_responses) {
        this.task_responses = this.task_responses.map((obj) => ensureObjectIdHelper(obj));
    }
    if (this.url_references) {
        this.url_references = this.url_references.map((obj) => ensureObjectIdHelper(obj));
    }
    if (this.user_interactions) {
        this.user_interactions = this.user_interactions.map((obj) => ensureObjectIdHelper(obj));
    }
    if (this.embeddings) {
        this.embeddings = this.embeddings.map((obj) => ensureObjectIdHelper(obj));
    }
    next();
}

function ensureObjectIdForUpdate(
    this: mongoose.Query<any, any>,
    next: mongoose.CallbackWithoutResultAndOptionalError
  ) {
    const update = this.getUpdate() as any;
    if (update.messages) {
        update.messages = update.messages.map((obj: any) => ensureObjectIdHelper(obj));
    }
    if (update.files) {
        update.files = update.files.map((obj: any) => ensureObjectIdHelper(obj));
    }
    if (update.task_responses) {
        update.task_responses = update.task_responses.map((obj: any) => ensureObjectIdHelper(obj));
    }
    if (update.url_references) {
        update.url_references = update.url_references.map((obj: any) => ensureObjectIdHelper(obj));
    }
    if (update.user_interactions) {
        update.user_interactions = update.user_interactions.map((obj: any) => ensureObjectIdHelper(obj));
    }
    if (update.embeddings) {
        update.embeddings = update.embeddings.map((obj: any) => ensureObjectIdHelper(obj));
    }
    next();
};

referencesSchema.plugin(mongooseAutopopulate);
referencesSchema.pre('save', ensureObjectIdForSave);
referencesSchema.pre('findOneAndUpdate', ensureObjectIdForUpdate);
export const DataCluster = mongoose.model<IDataClusterDocument, IDataClusterModel>('DataCluster', referencesSchema);