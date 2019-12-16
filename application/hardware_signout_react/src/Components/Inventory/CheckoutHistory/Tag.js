import React, { PureComponent } from 'react'
import styles from './checkoutHistory.module.scss'

export default class Tag extends PureComponent {
    render () {
        return (
            <div className={styles.historyLeftTagsListItem}>
                <p>{this.props.children}</p>
            </div>
        )
    }
}


