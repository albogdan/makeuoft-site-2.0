import React, { PureComponent } from 'react'
import styles from './overviewCard.module.scss';

export default class OverviewCard extends PureComponent {
    render() {
        let { ombre, value } = this.props;

        return (
            <div className={`${styles.overview} ${styles[`${ombre}`]}`}>
               <p>{value}</p>
            </div>
        )
    }
}
