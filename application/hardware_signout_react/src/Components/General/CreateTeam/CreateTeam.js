import React, { PureComponent } from 'react'
import styles from './createTeam.module.scss';
import AddTeamSelector from './../../Checkout/ItemSelector/AddTeamSelector';
import {ReactComponent as Close } from './../../../Assets/Images/Icons/x.svg'

export default class CreateTeam extends PureComponent {
    constructor(props) {
      super(props);
      this.state = { addTeamMembers: [], alertStyle: "", idAlert: false }
    }
    addTeam(){
        console.log("team???????", this.state.addTeamMembers);
        const { addTeamMembers } = this.state;
        let idFlag = false;

        for (let i=0; i<addTeamMembers.length; i++ ) {
            if (addTeamMembers[i].governmentID) {
                idFlag = true;
                break;
            }
        }

        if (idFlag === false) {
            this.setState({ idAlert: true });
            return;
        } else if (addTeamMembers.length < 2) {
            this.setState({ alertStyle: styles.alert, idAlert: false });
        } else {
            fetch('https://ieee.utoronto.ca/makeuoft/api/manageteams/addrecord', {
                method: "POST",
                body: JSON.stringify(addTeamMembers)
            })
            .then(function(response) {
                console.log(response);
            })
            .then(function(data){
                console.log(data);
            });

            this.props.close();
        }
    }

    addToTeam = (evt, index) => {
        this.setState(state => {
            let found = false;
            const addTeamMembers = state.addTeamMembers.map((item, j) => {
            if (j === index) {
                item.label = evt.label;
                item.value = evt.value;
                item.governmentID = false;
                found = true;
                return item;
            } else {
                return item;
            }});
            if (!found) {
                addTeamMembers.push({label: evt.label, value: evt.value, governmentID: false})
            }
            return { addTeamMembers };
        });
    }
    checkIdBox = index => {
        this.setState(state => {
            const addTeamMembers = state.addTeamMembers.map((item, j) => {
            if (j === index-1) {
                item.governmentID = !item.governmentID;
                return item;
            } else {
                return item;
            }});
            return { addTeamMembers };
        });
    }

    render() {
        let { close } = this.props;
        let { addTeamMembers, alertStyle, idAlert } = this.state;

        let memberField = [];
        for (let i=1; i<5; i++) {
            memberField.push(
                <div className={styles.popupCardMember}>
                    <label for={`member-${i}`} className={styles.popupCardMemberLabel}>Member {i}:</label>
                    <AddTeamSelector
                        id={`member-${i}`}
                        index={i}
                        addToTeam={this.addToTeam}
                        />
                    <label for={`id-${i}`} className={styles.popupCardMemberIDLabel}>ID: </label>
                    <input type="checkbox" id={`id-${i}`} onClick={()=> this.checkIdBox(i)} />
                </div>
            )
        }

        return (
            <div className={styles.overlay}>
                <div className={styles.popup} onClick={close}></div>
                <div className={styles.popupCard}>
                    <Close onClick={close} className={styles.popupCardClose} />
                    <p className={styles.popupCardHeading}>Create Team</p>
                    <p className={`${styles.popupCardMsg} ${alertStyle}`}>Teams must have at least 2 members decided when signing up their team</p>
                    {idAlert &&
                        <p className={`${styles.popupCardMsg} ${styles.alert}`} style={{marginTop: "-1rem"}}>At least 1 member has to provide their id</p>
                    }
                    {console.log("addTeamMembers", addTeamMembers) }
                    {memberField}
                    <button className={styles.popupCardBtn} onClick={() => this.addTeam()}>Add Team</button>
                </div>
            </div>
        )
    }
}
