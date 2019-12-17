import React, { PureComponent } from 'react'
import styles from './teamOverview.module.scss';
import { Accordion, AccordionItem, AccordionItemHeading, AccordionItemPanel, AccordionItemButton } from 'react-accessible-accordion';
import TeamOverviewAccordion  from './../../Components/TeamOverview/TeamOverviewAccordion/TeamOverviewAccordion';
import BasketItem from '../../Components/Checkout/BasketItem/BasketItem';
import { ReactComponent as Edit } from './../../Assets/Images/Icons/edit-symbol.svg';
import ListItem from './../../Components/Inventory/CheckoutHistory/CheckoutHistoryListItem';
import { Link } from 'react-router-dom';

export default class teamOverview extends PureComponent {
  constructor(props) {
    super(props);
    this.state = { };
  }

  render() {
    let teamNumber = JSON.parse(localStorage.getItem('viewThisTeam'));

    return (
      <div className={styles.overview}>
        <h2>Team Overview</h2>

        <div className={styles.overviewTeam}>
          <p style={{fontWeight: 600}}>Team {teamNumber}: &nbsp;</p>

          {/* Please map thru the team member names */}
          <span>Lisa Li</span>
          <span>Martin Ffrench</span>
          <span>Alex Bogdan</span>
          <span>Raghav Sirikajfkjhkjhk</span>

          {/* <Edit onClick={() => {openPopup("edit"); changePopupTeam(teamNumber)}}/> */}
        </div>

        <Accordion className={styles['accordion']} allowZeroExpanded={true} allowMultipleExpanded={true}  preExpanded={["checkout"]}> 
          <TeamOverviewAccordion heading={"Checked Out Items"}>
            <div className={styles.checkoutTable}>
              <p>Component</p>
              <p>Quantity</p>
            </div>

            <BasketItem component="Arduino" quantity={5} />
            <BasketItem component="Arduino" quantity={5} />
            <BasketItem component="Arduino" quantity={5} />
            <BasketItem component="Arduino" quantity={5} />

            <Link to={'/return-items'} style={{alignSelf: "flex-end"}}>
              <button>Return their stuff</button>
            </Link>

          </TeamOverviewAccordion>
          <TeamOverviewAccordion heading={"Returned Items"}>
            <div className={styles.historyRightTable}>
                <p>Component</p>
                <p>Quantity</p>
                <p>Time</p>
            </div>

            <ListItem isOverView={true} component="Arduino" quantity={5} time="March 29, 9:45 PM" />
            <ListItem isOverView={true} component="Arduino" quantity={5} time="March 29, 9:45 PM" />
            <ListItem isOverView={true} component="Arduino" quantity={5} time="March 29, 9:45 PM" />
            <ListItem isOverView={true} component="Arduino" quantity={5} time="March 29, 9:45 PM" />
            <ListItem isOverView={true} component="Arduino" quantity={5} time="March 29, 9:45 PM" />
            
          </TeamOverviewAccordion>
        </Accordion>
      </div>
    )
  }
}
