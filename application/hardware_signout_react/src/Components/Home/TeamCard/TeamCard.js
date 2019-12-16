import React, { PureComponent } from 'react'
import styles from './teamCard.module.scss';
import { Link } from 'react-router-dom';
import { ReactComponent as Edit } from './../../../Assets/Images/Icons/edit-symbol.svg';
import { ReactComponent as Check } from './../../../Assets/Images/Icons/checkmark.svg';
import { ReactComponent as Alert } from './../../../Assets/Images/Icons/alert.svg';

export default class TeamCard extends PureComponent {
    SaveTeamToLocal () {
        let viewTeam =  JSON.stringify(this.props.teamNumber)
        localStorage.setItem('viewThisTeam', viewTeam);
    }

    render() {
        let {teamNumber, members, openPopup, changePopupTeam} = this.props;
        return (
            <div className={styles.card}>
                <div className={styles.cardTitle}>
                    <p>Team {teamNumber}</p>
                    <Edit onClick={() => {openPopup("edit"); changePopupTeam(teamNumber)}}/>
                </div>
                <div className={styles.cardMembers}>
                    {members.map((item, i) =>
                        <div className={styles.cardMembersName}>
                            <p>{item.name}</p>
                            {item.govt_id ? <Check /> : <Alert />}
                        </div>
                    )}
                </div>
                <div className={styles.cardButton}>
                    <Link to={{pathname:'/checkout', state: {teamNumber: teamNumber}}}>
                        <button className={styles.cardButton1} >Add to cart</button>
                    </Link>
                    <Link to={'/team-overview'} onClick={()=>this.SaveTeamToLocal()}>
                        <button className={styles.cardButton2}>View cart</button>
                    </Link>
                </div>
            </div>
        )
    }
}
