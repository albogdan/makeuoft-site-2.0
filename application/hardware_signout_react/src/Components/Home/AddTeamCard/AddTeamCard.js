import React, { PureComponent } from 'react'
import styles from './../TeamCard/teamCard.module.scss';
import { ReactComponent as AddTeam } from './../../../Assets/Images/Icons/addTeam.svg';

export default class AddTeamCard extends PureComponent {
    render() {
        let { open } = this.props;
        return (
            <div className={`${styles.card} ${styles.addCard}`} onClick={open}>
                <AddTeam />
                <p>Add Team</p>
            </div>
        )
    }
}
