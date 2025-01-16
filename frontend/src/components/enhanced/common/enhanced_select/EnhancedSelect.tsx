import React, { useCallback, useMemo } from 'react';
import { Box, IconButton, Chip, Tooltip, FormControl, InputLabel } from '@mui/material';
import { Edit, Add, Info } from '@mui/icons-material';
import { useDialog } from '../../../../contexts/DialogContext';
import useStyles from './EnhancedSelectStyles';
import { CollectionName, CollectionType, CollectionElementString, collectionNameToElementString, collectionNameToEnhancedComponent } from '../../../../types/CollectionTypes';
import theme from '../../../../Theme';
import BorderedContainer from '../inputs/BorderContainer';
import Logger from '../../../../utils/Logger';

interface EnhancedSelectProps<T extends CollectionType[CollectionName]> {
  componentType: CollectionName;
  EnhancedView: React.ComponentType<any>;
  selectedItems: T[];
  onSelect: (selectedItems: T[]) => void;
  isInteractable: boolean;
  multiple?: boolean;
  label: string;
  activeAccordion?: string | null;
  onAccordionToggle?: (accordionName: string | null) => void;
  onView?: (id: string) => void;
  showCreateButton?: boolean;
  description?: string;
  filters?: Record<string, any>;
}

function EnhancedSelect<T extends CollectionType[CollectionName]>({
  componentType,
  EnhancedView,
  selectedItems,
  onSelect,
  isInteractable,
  multiple = false,
  label,
  showCreateButton = false,
  description,
  filters
}: EnhancedSelectProps<T>) {
  const classes = useStyles();
  const { selectFlexibleItem, selectCardItem, selectEnhancedOptions } = useDialog();
  const [ items, setItems ] = React.useState<T[]>(selectedItems);
  const collectionElementString = collectionNameToElementString[componentType] as CollectionElementString;
  const elementEnhanced = collectionNameToEnhancedComponent[componentType];

  const localOnSelect = useCallback((selectedItems: T[]) => {
    setItems(selectedItems);
    onSelect(selectedItems);
  }, [onSelect]);

  const handleOpenOptions = useCallback(() => {
    selectEnhancedOptions(
      componentType,
      elementEnhanced,
      label,
      (selectedItem: T) => {
        Logger.info('EnhancedSelect - handleOpenOptions - selected item:', selectedItem, items);
        if (multiple) {
          // For multiple selection, merge with existing items
          const uniqueItems = [...items];
          if (!uniqueItems.some(item => item._id === selectedItem._id)) {
              uniqueItems.push(selectedItem);
          }
          localOnSelect(uniqueItems);
        } else {
          localOnSelect([selectedItem]);
        }
      },
      multiple,
    );
  }, [componentType, elementEnhanced, label, localOnSelect, multiple, selectEnhancedOptions, items]);

  const handleCreate = useCallback(() => {
    selectFlexibleItem(collectionElementString, 'create');
  }, [selectFlexibleItem, collectionElementString]);

  const handleDelete = useCallback((itemToDelete: T) => {
    const updatedItems = items
      .filter(item => item._id !== itemToDelete._id)
    localOnSelect(updatedItems);
  }, [items, localOnSelect]);

  const commonProps = useMemo(() => ({
    items: null,
    onChange: () => { },
    mode: 'view',
    handleSave: async () => undefined,
  }), []);

  const renderSelectedItem = useCallback((item: T) => (
    <Chip
      key={item._id}
      label={<EnhancedView item={item} {...commonProps} />}
      onDelete={multiple && isInteractable ? () => handleDelete(item) : undefined}
      onClick={() => selectCardItem(collectionElementString, item._id!)}
      className={classes.chip}
    />
  ), [classes.chip, isInteractable, multiple, selectCardItem, collectionElementString, commonProps, EnhancedView, handleDelete]);

  return (
    <FormControl fullWidth variant="outlined" sx={{ marginTop: 1, marginBottom: 1 }}>
      <InputLabel shrink sx={{ backgroundColor: theme.palette.primary.dark }}>
        {label}{multiple ? ' (multiple)' : null}
      </InputLabel>
      <BorderedContainer>
        <Box sx={{
          display: 'flex',
          flexDirection: { xs: 'column', sm: 'row' },
          gap: 1,
          minHeight: '48px'
        }}>
          <Box sx={{
            flex: 1,
            display: 'flex',
            flexWrap: 'wrap',
            gap: 1,
            alignItems: 'center',
            minHeight: '40px'
          }}>
            {items?.map(renderSelectedItem)}{items.length === 0 && 'None'}
          </Box>

          <Box sx={{
            display: 'flex',
            gap: 1,
            alignItems: 'center',
            justifyContent: { xs: 'flex-start', sm: 'flex-end' },
            padding: '4px'
          }}>
            {description && (
              <Tooltip title={description}>
                <IconButton size="small">
                  <Info fontSize="small" />
                </IconButton>
              </Tooltip>
            )}
            <Tooltip title={isInteractable ? 'Select Items' : ''}>
              <span>
                <IconButton
                  onClick={handleOpenOptions}
                  disabled={!isInteractable}
                  size="small"
                  className={classes.editButton}
                >
                  <Edit fontSize="small" />
                </IconButton>
              </span>
            </Tooltip>
            {showCreateButton && (
              <Tooltip title={isInteractable ? 'Create New' : ''}>
                <span>
                  <IconButton
                    onClick={handleCreate}
                    disabled={!isInteractable}
                    size="small"
                    className={classes.createButton}
                  >
                    <Add fontSize="small" />
                  </IconButton>
                </span>
              </Tooltip>
            )}
          </Box>
        </Box>
      </BorderedContainer>
    </FormControl>
  );
}

export default EnhancedSelect;