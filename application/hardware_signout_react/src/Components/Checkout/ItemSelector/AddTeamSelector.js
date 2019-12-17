import React, { PureComponent } from 'react';
import styles from './itemSelector.module.scss';
import Select from 'react-select';
import { colourStyles } from './SelectorStyles'

export default class ItemSelector extends PureComponent {
    constructor(props) {
        super(props);
        this.state = { selectedOption: null, participants:null}
        this.handleChange = this.handleChange.bind(this)
        fetch('https://ieee.utoronto.ca/makeuoft/api/manageteams/getparticipants',{
          method: "POST"
        })
          .then(response => response.json())
          .then(participants => this.setState({ participants }));
    }

    handleChange = selectedOption => {
        this.setState({ selectedOption });
    };

    render() {
        let { selectedOption, participants } = this.state;
        let { id, index, addToTeam } = this.props;

        return (
            <Select
                value={selectedOption}
                className={styles.team}
                styles={colourStyles}
                id={id}
                onChange={(evt) => {this.handleChange(); addToTeam(evt, index)}}
                options={participants}
                isClearable={true}
            />
        );
    }
}
