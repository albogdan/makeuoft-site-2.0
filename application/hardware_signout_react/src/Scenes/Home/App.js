import React, { PureComponent } from 'react'
import styles from './App.module.scss';
import TeamCard from './../../Components/Home/TeamCard/TeamCard';
import AddTeamCard from '../../Components/Home/AddTeamCard/AddTeamCard';
import OverviewCard from '../../Components/Home/OverviewCard/OverviewCard';
import CreateTeam from '../../Components/General/CreateTeam/CreateTeam';
import EditTeam from '../../Components/General/CreateTeam/EditTeam';

export default class App extends PureComponent {
  constructor(props) {
    super(props);
    this.state = {
      addTeamPopup: false,
      editPopup: false,
      editPopupTeam: null,
      test: undefined,
      teams: null,
      info: null
    };
    fetch('http://localhost:8181/api/teamlist')
      .then(response => response.json())
      .then(teams => this.setState({ teams }));
    fetch('http://localhost:8181/api/info')
      .then(response => response.json())
      .then(info => this.setState({ info }));
  }

  openPopup = type => {
    if (type === "addTeam") {
      this.setState({addTeamPopup: true});
    } else if (type === "edit") {
      this.setState({editPopup: true});
    }
  }

  closePopup() {
    this.setState({addTeamPopup: false, editPopup: false});
  }

  changePopupTeam = index => {
    this.setState({editPopupTeam: index});
  }

  render() {
    let { addTeamPopup, teams, info, editPopup, editPopupTeam } = this.state;
    const teamsDataReceived = (teams===null);
    const infoDataReceived = (info===null);

    return (
      <div className={styles.home}>
        {addTeamPopup &&
          <CreateTeam close={() => {this.closePopup()}} />
        }
        {editPopup &&
          <EditTeam teamNumber={editPopupTeam} close={() => {this.closePopup()}}/>
        }
        <h1 style={{marginTop: 50}}>MakeUofT Hardware Signout</h1>

        <div className={styles.overview}>
          <h2>Overview</h2>

          <div className={styles.teamList}>
            {infoDataReceived ? (
                <OverviewCard ombre="orange" value="Loading..."/>
            ) : (
              <React.Fragment>
                <OverviewCard ombre="blue" value={ `${info.partsout} / ${info.partsall} parts out` }/>
                <OverviewCard ombre="orange" value={ `${info.teamcount} Teams` }/>
                <OverviewCard ombre="purple" value={ `${info.usercount} Participants` }/>
              </React.Fragment>
            )}
          </div>
        </div>

        <div className={styles.team}>
          <h2>Teams</h2>

          <div className={styles.teamList}>
            <AddTeamCard open={() => this.openPopup("addTeam")} />
            {teamsDataReceived ? (
                <p className={styles.inventoryListLoading}>Loading...</p>
            ) : (
              teams.map((item, i) => {
                return (
                  <TeamCard teamNumber={item.index} members={item.members} openPopup={this.openPopup} changePopupTeam={this.changePopupTeam}/>
                )
              })
            )}
          </div>
        </div>
      </div>
    )
  }
}
