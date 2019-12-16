import React, { PureComponent } from 'react'
import styles from './checkoutHistory.module.scss';
import {ReactComponent as Close } from './../../../Assets/Images/Icons/x.svg'
import Component from './../Component/Component';
import ListItem from './CheckoutHistoryListItem';
import Tag from './Tag';

export default class CheckoutHistory extends PureComponent {
    constructor(props) {
        super(props);
        this.state = { components: null}
        fetch('http://localhost:8282/api/inventory')
          .then(response => response.json())
          .then(components => this.setState({ components }));
    }

    render() {
        let { close, event } = this.props;
        return (
            
            <div className={styles.overlay}>
                <div className={styles.popup} onClick={close}></div>
                <div className={styles.history}>
                    <Close onClick={close} />
                    <div className={styles.historyLeft}>
                        <Component item={event.name} total={event.total} left={event.available} isCheckout={true} />

                        <div className={styles.historyLeftTags}>
                            <p className={styles.historyLeftTagsTag}>Tags:</p>
                            <div className={styles.historyLeftTagsList}>
                                {event.tags.map((item, i) =>
                                    <Tag>{item}</Tag>
                                )}
                            </div>
                        </div>
                    </div>
                    <div className={styles.historyRight}>
                        <h3>Checkout History</h3>
                        <div className={styles.historyRightTable}>
                            <p>Team</p>
                            <p>Quantity</p>
                            <p>Time</p>
                        </div>

                        <ListItem number={1} members={["Lisa Li", "Karen Zhao", "Alex Bogdan", "Martin Ffrench"]} quantity={5} time="March 29, 9:45 PM" />
                        <ListItem number={2} members={["Lisa", "Karen", "Alex", "Martin"]} quantity={5} time="March 29, 9:45 PM" />
                        <ListItem number={3} members={["Lisa", "Karen", "Alex", "Martin"]} quantity={5} time="March 29, 9:45 PM" />
                        <ListItem number={4} members={["Lisa", "Karen", "Alex", "Martin"]} quantity={5} time="March 29, 9:45 PM" />
                        <ListItem number={1} members={["Lisa Li", "Karen Zhao", "Alex Bogdan", "Martin Ffrench"]} quantity={5} time="March 29, 9:45 PM" />
                        <ListItem number={2} members={["Lisa", "Karen", "Alex", "Martin"]} quantity={5} time="March 29, 9:45 PM" />
                        <ListItem number={3} members={["Lisa", "Karen", "Alex", "Martin"]} quantity={5} time="March 29, 9:45 PM" />
                        <ListItem number={4} members={["Lisa", "Karen", "Alex", "Martin"]} quantity={5} time="March 29, 9:45 PM" />
                    </div>
                </div>
            </div>
        )
    }
}

