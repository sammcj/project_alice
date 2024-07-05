import React from 'react';
import AgentFlexibleView from './AgentFlexibleView';
import AgentListView from './AgentListView';
import AgentTableView from './AgentTableView';
import AgentCardView from './AgentCardView';
import { AliceAgent } from '../../../utils/AgentTypes';
import BaseDbElement, { BaseDbElementProps } from '../../BaseDbElement';
import { AgentComponentProps } from '../../../utils/AgentTypes';

type BaseAgentMode = BaseDbElementProps<AliceAgent>['mode'];
type ExtendedAgentMode = 'list' | 'shortList' | 'card' | 'table';
type EnhancedAgentMode = BaseAgentMode | ExtendedAgentMode;

interface EnhancedAgentProps extends Omit<AgentComponentProps, 'items' | 'item' | 'onChange' | 'handleSave' | 'mode'> {
  mode: EnhancedAgentMode;
  itemId?: string;
  fetchAll: boolean;
  onSave?: (savedItem: AliceAgent) => void;
  onAddAgent?: () => void;
}

const EnhancedAgent: React.FC<EnhancedAgentProps> = (props) => {
  const renderContent = (
    items: AliceAgent[] | null,
    item: AliceAgent | null,
    onChange: (newItem: Partial<AliceAgent>) => void,
    mode: BaseAgentMode,
    handleSave: () => Promise<void>
  ) => {
    const commonProps: AgentComponentProps = {
      items,
      item,
      onChange,
      mode,
      handleSave,
      isInteractable: props.isInteractable,
      onInteraction: props.onInteraction,
      showHeaders: props.showHeaders,
    };

    switch (props.mode) {
      case 'create':
      case 'edit':
      case 'view':
        return <AgentFlexibleView {...commonProps} />;
      case 'list':
      case 'shortList':
        return <AgentListView {...commonProps}/>;
      case 'table':
        return <AgentTableView {...commonProps} />;
      case 'card':
        return <AgentCardView {...commonProps} />;
      default:
        return null;
    }
  };

  const baseDbMode: BaseDbElementProps<AliceAgent>['mode'] =
    props.mode === 'create' ? 'create' :
    props.mode === 'edit' ? 'edit' : 'view';

  return (
    <BaseDbElement<AliceAgent>
      collectionName="agents"
      itemId={props.itemId}
      mode={baseDbMode}
      isInteractable={props.isInteractable}
      onInteraction={props.onInteraction}
      onSave={props.onSave}
      fetchAll={props.fetchAll}
      render={renderContent}
    />
  );
};

export default EnhancedAgent;