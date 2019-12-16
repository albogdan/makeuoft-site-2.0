import React, { PureComponent } from 'react';
import styles from './itemSelector.module.scss';
import Select from 'react-select';
import { colourStyles } from './SelectorStyles'
import { groupStyles, groupBadgeStyles } from './SelectorStyles'

const formatGroupLabel = data => (
    <div style={groupStyles}>
        <span>{data.label}</span>
        <span style={groupBadgeStyles}>{data.options.length}</span>
    </div>
);

export default class ItemSelector extends PureComponent {
    constructor(props) {
        super(props);
        this.state = { selectedOption: null, isClearable: true}
        this.handleChange = this.handleChange.bind(this)
    }

    handleChange = selectedOption => {
        this.setState({ selectedOption });
    };

    render() {
        let { selectedOption } = this.state;
        let { type, options, defaultValue, selectItem, fieldIndex, selectTeam, selectedValue } = this.props;
        
        let style = (type === "team") ? styles.team : styles.component;

        let onBlur;
        if (type === "team") {
            onBlur = () => selectTeam(selectedOption);
        } else if (type === "component") {
            onBlur = (evt, index) => selectItem(selectedOption, fieldIndex)
        }

        return (
            <Select
                value={selectedValue}
                onChange={this.handleChange}
                onBlur={onBlur}
                className={style}
                styles={colourStyles}

                options={options}
                formatGroupLabel={formatGroupLabel}
                defaultValue={defaultValue}
            />
        );
    }
}
