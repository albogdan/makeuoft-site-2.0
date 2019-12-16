
import React, { PureComponent } from 'react';
import styles from './itemSelector.module.scss';
import Select from 'react-select';
import { colourStyles } from './SelectorStyles';

export default class BasketItem extends PureComponent {
    constructor(props) {
        super(props);
        this.state = { selectedOption: null }
    }

    handleChange = evt => {
        this.setState({ selectedOption: evt });
    };

    componentWillUpdate(nextProps, nextState) {
        if ((this.props.selectedHardware) && (this.props.selectedHardware.label !== nextProps.selectedHardware.label)) {
            this.setState({ selectedOption: null });
        }
    }
   
    render() {
        let {selectQuantity, fieldIndex, options, selectedValue, onChange } = this.props

        return (
            <Select
                value={selectedValue}
                onChange={(evt) => {this.handleChange(); onChange(evt, fieldIndex)}}
                onBlur={() => selectQuantity(fieldIndex)}
                className={styles.quantity}
                styles={colourStyles}
                options={options}
                placeholder={""}
            />
        );
    }
}
