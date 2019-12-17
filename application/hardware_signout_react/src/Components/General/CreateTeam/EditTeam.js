import React, { PureComponent } from 'react'
import styles from './createTeam.module.scss';
import EditTeamSelector from './../../Checkout/ItemSelector/EditTeamSelector';
import {ReactComponent as Close } from './../../../Assets/Images/Icons/x.svg'

export default class CreateTeam extends PureComponent {
    constructor(props) {
      super(props);
      this.state = { teamMembers: null, deleteConfirm: false }
      fetch('http://localhost:8181/api/manageteams/getmembers', {
          method: "POST",
          body: JSON.stringify({"teamNumber": this.props.teamNumber})
        })
          .then(response => response.json())
          .then(teamMembers => this.setState({ teamMembers }));

    }

    deleteTeamLayerOne() {
        this.setState({ deleteConfirm: !this.state.deleteConfirm })
    }

    deleteTeamLayerTwo() {
      fetch('http://localhost:8181/api/manageteams/deleteteam', {
          method: "POST",
          body: JSON.stringify({"teamNumber":this.props.teamNumber})
      })
      .then(function(response) {
          console.log(response);
      })
      .then(function(data){
          console.log(data);
      });

      this.props.close();
    }


    render() {
        let { close, teamNumber } = this.props;
        let { deleteConfirm, idAlert, teamMembers } = this.state;
        console.log("MEMBERS", teamMembers);
        let memberField = [];
        for (let i=1; i<5; i++) {
            memberField.push(
                <div className={styles.popupCardMember}>
                    <label for={`member-${i}`} className={styles.popupCardMemberLabel}>Member {i}:</label>
                    <EditTeamSelector
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
                {deleteConfirm &&
                    <div className={styles.popupCard} style={{zIndex: 11, position: "absolute", height: 392}}>
                        <p className={styles.popupCardHeading} style={{marginBottom: 25}}>BITCH ARE U SURE?????????</p>
                        <p className={styles.popupCardMsg}>Lisa and Martin will whoop yo ass if u f*** dis up.</p>
                        <button className={styles.deleteTeamBtn} onClick={()=>this.deleteTeamLayerTwo()} style={{alignSelf: "center", marginBottom: 20}}>I said D  E  L  E  T  E</button>
                        <button className={styles.popupCardBtn} onClick={()=>this.deleteTeamLayerOne()}>Take me back pls im dumb</button>
                    </div>

                }
                <div className={styles.popup} onClick={close}></div>
                <div className={styles.popupCard}>
                    <Close onClick={close} className={styles.popupCardClose} />
                    <p className={styles.popupCardHeading} style={{marginBottom: 25}}>Edit Team {teamNumber}</p>
                    {idAlert &&
                        <p className={`${styles.popupCardMsg} ${styles.alert}`}>At least 1 member has to provide their id</p>
                    }
                    {memberField}
                    <button className={styles.popupCardBtn}>Save edit</button>
                    <button className={styles.deleteTeamBtn} onClick={() => this.deleteTeamLayerOne()}>DELETE TEAM</button>
                </div>
            </div>
        )
    }
}
